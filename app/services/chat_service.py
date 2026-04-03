from app.core.config import Settings
from app.providers.base import LlmProvider, ProviderChatRequest
from app.schemas.chat import ChatRequest, ChatResponse

class ChatService:
    def __init__(self, settings: Settings, provider: LlmProvider):
        self._settings = settings
        self._provider = provider

    async def generate_chat_response(self, request: ChatRequest) -> ChatResponse:
        provider_request = ProviderChatRequest(
            messages=request.messages,
            model=self._settings.openai_model_chat,
            temperature=request.temperature,
            max_output_tokens=request.max_output_tokens
        )

        provider_result = await self._provider.chat(provider_request)

        if not provider_result.content.strip():
            raise RuntimeError("Provider returned an empty chat content.")

        return ChatResponse(
            content=provider_result.content,
            model=provider_result.model,
            provider=self._settings.openai_provider,
            request_id=provider_result.request_id,
            usage=provider_result.usage
        )