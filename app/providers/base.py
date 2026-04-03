from typing import Protocol

from pydantic import BaseModel, Field

from app.schemas.chat import ChatMessage, UsageInfo


class ProviderChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1)
    model: str
    temperature: float | None = Field(default=None, ge=0, le=2)
    max_output_tokens: int | None = Field(default=None)


class ProviderTextResult(BaseModel):
    content: str
    model: str
    request_id: str | None = None
    usage: UsageInfo | None = None


class LlmProvider(Protocol):
    async def chat(self, request: ProviderChatRequest) -> ProviderTextResult:
        ...
