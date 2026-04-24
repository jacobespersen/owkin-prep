import pytest
from app.schemas.chat import ChatRequest, ChatResponse
from pydantic import ValidationError

VALID_API_KEY = (
    "sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    "-xxxxxxxxxxxx-xxxxxxxxAAAA"
)


def test_valid_api_key():
    req = ChatRequest(api_key=VALID_API_KEY, messages=[])
    assert req.api_key.get_secret_value() == VALID_API_KEY


def test_api_key_stripped():
    req = ChatRequest(api_key=f"  {VALID_API_KEY}  ", messages=[])
    assert req.api_key.get_secret_value() == VALID_API_KEY


def test_api_key_not_exposed_in_repr():
    req = ChatRequest(api_key=VALID_API_KEY, messages=[])
    assert VALID_API_KEY not in repr(req)


def test_invalid_api_key_format():
    with pytest.raises(ValidationError):
        ChatRequest(api_key="invalid-key", messages=[])


def test_empty_api_key():
    with pytest.raises(ValidationError):
        ChatRequest(api_key="", messages=[])


def test_chat_response():
    resp = ChatResponse(response="Hello")
    assert resp.response == "Hello"
