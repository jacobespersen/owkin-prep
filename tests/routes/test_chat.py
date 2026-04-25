from unittest.mock import MagicMock, patch

import anthropic
from app.main import app
from fastapi.testclient import TestClient


def _mock_response(status_code=401):
    resp = MagicMock()
    resp.status_code = status_code
    resp.request = MagicMock()
    return resp


VALID_API_KEY = (
    "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    "-xxxxxxxxxxxx-xxxxxxxxAAAA"
)

client = TestClient(app)


def test_chat_invalid_api_key():
    response = client.post("/chat", json={"api_key": "bad-key", "messages": []})
    assert response.status_code == 422


@patch("app.routes.chat.run_agent_loop", return_value="Hello!")
def test_chat_success(mock_agent):
    response = client.post(
        "/chat",
        json={
            "api_key": VALID_API_KEY,
            "messages": [{"role": "user", "content": "Hi"}],
        },
    )
    assert response.status_code == 200
    assert response.json() == {"response": "Hello!"}
    mock_agent.assert_called_once()


@patch(
    "app.routes.chat.run_agent_loop",
    side_effect=RuntimeError("Loop exceeded"),
)
def test_chat_agent_error(mock_agent):
    response = client.post(
        "/chat",
        json={
            "api_key": VALID_API_KEY,
            "messages": [{"role": "user", "content": "Hi"}],
        },
    )
    assert response.status_code == 500


@patch(
    "app.routes.chat.run_agent_loop",
    side_effect=anthropic.AuthenticationError(
        message="invalid key", response=_mock_response(401), body=None
    ),
)
def test_chat_bad_api_key_returns_401(mock_agent):
    response = client.post(
        "/chat",
        json={
            "api_key": VALID_API_KEY,
            "messages": [{"role": "user", "content": "Hi"}],
        },
    )
    assert response.status_code == 401
    assert "Invalid API key" in response.json()["detail"]


@patch(
    "app.routes.chat.run_agent_loop",
    side_effect=anthropic.RateLimitError(
        message="rate limited", response=_mock_response(429), body=None
    ),
)
def test_chat_rate_limit_returns_429(mock_agent):
    response = client.post(
        "/chat",
        json={
            "api_key": VALID_API_KEY,
            "messages": [{"role": "user", "content": "Hi"}],
        },
    )
    assert response.status_code == 429
