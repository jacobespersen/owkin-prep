from unittest.mock import MagicMock, patch

import pytest
from app.services.agent import run_agent_loop
from pydantic import SecretStr


def _make_text_response(text):
    """Create a mock Anthropic response with a text block."""
    block = MagicMock()
    block.type = "text"
    block.text = text
    response = MagicMock()
    response.stop_reason = "end_turn"
    response.content = [block]
    return response


def _make_tool_use_response(tool_name, tool_input, tool_id="call_1"):
    """Create a mock Anthropic response with a tool_use block."""
    block = MagicMock()
    block.type = "tool_use"
    block.name = tool_name
    block.input = tool_input
    block.id = tool_id
    response = MagicMock()
    response.stop_reason = "tool_use"
    response.content = [block]
    response.model_dump.return_value = {
        "content": [
            {
                "type": "tool_use",
                "id": tool_id,
                "name": tool_name,
                "input": tool_input,
            }
        ]
    }
    return response


@patch("app.services.agent.anthropic")
def test_direct_text_response(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_client.messages.create.return_value = _make_text_response("Hello!")

    result = run_agent_loop(SecretStr("fake-key"), [{"role": "user", "content": "Hi"}])
    assert result == "Hello!"


@patch("app.services.agent.execute_tool", return_value=["ALK", "KRAS"])
@patch("app.services.agent.anthropic")
def test_tool_use_then_text(mock_anthropic, mock_execute):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_client.messages.create.side_effect = [
        _make_tool_use_response("get_targets", {"cancer_name": "lung"}),
        _make_text_response("Lung cancer genes: ALK, KRAS"),
    ]

    result = run_agent_loop(
        SecretStr("fake-key"),
        [{"role": "user", "content": "lung genes?"}],
    )
    assert "ALK" in result
    mock_execute.assert_called_once_with("get_targets", {"cancer_name": "lung"})


@patch("app.services.agent.anthropic")
def test_max_iterations_exceeded(mock_anthropic):
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_client.messages.create.return_value = _make_tool_use_response(
        "get_targets", {"cancer_name": "lung"}
    )

    with pytest.raises(RuntimeError, match="max iterations"):
        run_agent_loop(
            SecretStr("fake-key"),
            [{"role": "user", "content": "Hi"}],
        )


@patch("app.services.agent.execute_tool", side_effect=ValueError("bad input"))
@patch("app.services.agent.anthropic")
def test_tool_error_sent_back_to_model(mock_anthropic, mock_execute):
    """When a tool raises, the error is sent back so the model can self-correct."""
    mock_client = MagicMock()
    mock_anthropic.Anthropic.return_value = mock_client
    mock_client.messages.create.side_effect = [
        _make_tool_use_response("get_targets", {"cancer_name": "lung"}),
        _make_text_response("Sorry, that tool failed."),
    ]

    result = run_agent_loop(
        SecretStr("fake-key"),
        [{"role": "user", "content": "lung genes?"}],
    )
    assert result == "Sorry, that tool failed."

    # Verify the tool result sent back had is_error=True
    second_call_messages = mock_client.messages.create.call_args_list[1]
    user_msg = second_call_messages.kwargs.get(
        "messages", second_call_messages[1].get("messages", [])
    )[-1]
    tool_result = user_msg["content"][0]
    assert tool_result["is_error"] is True
    assert "bad input" in tool_result["content"]
