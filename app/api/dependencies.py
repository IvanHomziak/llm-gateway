from fastapi import Depends

from app.core.config import Settings, get_settings
from app.providers.base import LlmProvider
from app.providers.openai_provider import OpenAIProvider
from app.services.chat_service import ChatService


def get_openai_provider(
        settings: Settings = Depends(get_settings),
) -> LlmProvider:
    return OpenAIProvider(settings)


def get_chat_service(
        settings: Settings = Depends(get_settings),
        provider: LlmProvider = Depends(get_openai_provider),
) -> ChatService:
    return ChatService(settings=settings, provider=provider)
