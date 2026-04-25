import json
import logging

import anthropic
from anthropic.types import MessageParam, ToolResultBlockParam
from pydantic import SecretStr

from app.services.tools import TOOL_DEFINITIONS, build_system_prompt, execute_tool

logger = logging.getLogger(__name__)

MAX_ITERATIONS = 10


def run_agent_loop(api_key: SecretStr, messages: list[MessageParam]) -> str:
    """Run the agent loop: call Claude, execute tools, repeat until text response."""
    messages = list(messages)
    client = anthropic.Anthropic(api_key=api_key.get_secret_value())
    system_prompt = build_system_prompt()

    user_message = messages[-1]["content"] if messages else "(empty)"
    logger.info("Agent loop started | user_message=%s", user_message)

    for iteration in range(1, MAX_ITERATIONS + 1):
        logger.info("Iteration %d/%d — calling Claude", iteration, MAX_ITERATIONS)

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        logger.info(
            "Claude responded | stop_reason=%s | content_blocks=%d"
            " | usage(in=%d, out=%d)",
            response.stop_reason,
            len(response.content),
            response.usage.input_tokens,
            response.usage.output_tokens,
        )

        if response.stop_reason == "end_turn":
            text_parts = [
                block.text for block in response.content if block.type == "text"
            ]
            final_text = "\n".join(text_parts)
            logger.info(
                "Agent loop finished | iterations=%d | response_length=%d chars",
                iteration,
                len(final_text),
            )
            return final_text

        messages.append(
            {"role": "assistant", "content": response.model_dump()["content"]}
        )

        tool_results: list[ToolResultBlockParam] = []
        for block in response.content:
            if block.type == "tool_use":
                logger.info(
                    "Executing tool | name=%s | input=%s",
                    block.name,
                    json.dumps(block.input),
                )
                try:
                    result = execute_tool(block.name, block.input)
                    content = json.dumps(result)
                    is_error = False
                    logger.info(
                        "Tool succeeded | name=%s | result=%s",
                        block.name,
                        content,
                    )
                except (ValueError, KeyError, TypeError) as e:
                    content = f"Tool execution failed: {e}"
                    is_error = True
                    logger.exception("Tool failed | name=%s | error=%s", block.name, e)
                tool_results.append(
                    ToolResultBlockParam(
                        type="tool_result",
                        tool_use_id=block.id,
                        content=content,
                        is_error=is_error,
                    )
                )

        logger.info("Sending %d tool result(s) back to Claude", len(tool_results))
        messages.append(MessageParam(role="user", content=tool_results))

    logger.error("Agent loop exceeded max iterations (%d)", MAX_ITERATIONS)
    raise RuntimeError("Agent loop exceeded max iterations")
