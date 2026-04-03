from openai import AsyncOpenAI

from app.core.config import Settings
from app.providers.base import ProviderChatRequest, ProviderTextResult, LlmProvider
from app.schemas.chat import UsageInfo


class OpenAIProvider:
    def __init__(self, settings: Settings):
        self._settings = settings
        self._client = AsyncOpenAI(api_key=self._settings.openai_api_key)

    async def chat(self, request: ProviderChatRequest) -> ProviderTextResult:
        input_messages = [
            {
                "role": message.role,
                "content": [
                    {
                        "type": "input_text",
                        "text": message.content,
                    }
                ],
            }
            for message in request.messages
        ]

        create_kwargs = {
            "model": request.model,
            "input": input_messages,
        }

        if request.temperature is not None:
            create_kwargs["temperature"] = request.temperature

        if request.max_output_tokens is not None:
            create_kwargs["max_output_tokens"] = request.max_output_tokens

        response = await self._client.responses.create(**create_kwargs)

        usage = None
        if getattr(response, "usage", None) is not None:
            usage = UsageInfo(
                input_tokens=getattr(response.usage, "input_tokens", None),
                output_tokens=getattr(response.usage, "output_tokens", None),
                total_tokens=getattr(response.usage, "total_tokens", None),
            )

        return ProviderTextResult(
            content=(response.output_text or "").strip(),
            model=request.model,
            request_id=getattr(response, "id", None),
            usage=usage,
        )