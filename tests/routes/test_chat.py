from unittest.mock import patch

from app.main import app
from fastapi.testclient import TestClient

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
