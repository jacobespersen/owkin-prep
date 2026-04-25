from anthropic.types import MessageParam
from pydantic import BaseModel, SecretStr, field_validator


class ChatRequest(BaseModel):
    api_key: SecretStr
    messages: list[MessageParam]

    @field_validator("api_key", mode="before")
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        v = v.strip()
        if "sk-ant-api" not in v:
            raise ValueError(
                "Invalid Anthropic API key format. Key must contain 'sk-ant-api'."
            )
        return v


class ChatResponse(BaseModel):
    response: str
