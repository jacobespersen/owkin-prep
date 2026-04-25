import json

import anthropic
from anthropic.types import MessageParam, ToolResultBlockParam
from pydantic import SecretStr

from app.services.tools import TOOL_DEFINITIONS, build_system_prompt, execute_tool

MAX_ITERATIONS = 10


def run_agent_loop(api_key: SecretStr, messages: list[MessageParam]) -> str:
    """Run the agent loop: call Claude, execute tools, repeat until text response."""
    messages = list(messages)
    client = anthropic.Anthropic(api_key=api_key.get_secret_value())
    system_prompt = build_system_prompt()

    for _ in range(MAX_ITERATIONS):
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=1024,
            system=system_prompt,
            tools=TOOL_DEFINITIONS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text_parts = [
                block.text for block in response.content if block.type == "text"
            ]
            return "\n".join(text_parts)

        messages.append(
            {"role": "assistant", "content": response.model_dump()["content"]}
        )

        tool_results: list[ToolResultBlockParam] = []
        for block in response.content:
            if block.type == "tool_use":
                try:
                    result = execute_tool(block.name, block.input)
                    content = json.dumps(result)
                    is_error = False
                except Exception as e:
                    content = f"Tool execution failed: {e}"
                    is_error = True
                tool_results.append(
                    ToolResultBlockParam(
                        type="tool_result",
                        tool_use_id=block.id,
                        content=content,
                        is_error=is_error,
                    )
                )

        messages.append(MessageParam(role="user", content=tool_results))

    raise RuntimeError("Agent loop exceeded max iterations")
