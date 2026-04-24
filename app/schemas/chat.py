import re

from pydantic import BaseModel, SecretStr, field_validator


class ChatRequest(BaseModel):
    api_key: SecretStr
    messages: list[dict]

    @field_validator("api_key", mode="before")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        v = v.strip()
        if not re.match(r"^sk-ant-api03-[A-Za-z0-9_-]+$", v):
            raise ValueError(
                "Invalid Anthropic API key format. Expected 'sk-ant-api03-...'"
            )
        return v


class ChatResponse(BaseModel):
    response: str
