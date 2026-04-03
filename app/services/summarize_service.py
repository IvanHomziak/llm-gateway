from app.core.config import Settings
from app.providers.base import (
    LlmProvider,
    ProviderSummarizeRequest,
)
from app.schemas.summarize import SummarizeRequest, SummarizeResponse


class SummarizeService:
    def __init__(self, settings: Settings, provider: LlmProvider):
        self._settings = settings
        self._provider = provider

    async def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        provider_request = ProviderSummarizeRequest(
            text=request.text,
            instructions=self._build_instructions(request),
            model=self._settings.openai_model_summarize,
        )

        provider_result = await self._provider.summarize(provider_request)

        return SummarizeResponse.model_validate(provider_result.data)

    @staticmethod
    def _build_instructions(request: SummarizeRequest) -> str:
        style_map = {
            "executive": (
                "Write a concise executive summary with clear business-oriented language."
            ),
            "bullet": (
                "Write a compact bullet-oriented summary optimized for quick scanning."
            ),
            "technical": (
                "Write a technical summary with precise engineering language and explicit details."
            ),
        }

        language_map = {
            "uk": "Ukrainian",
            "en": "English",
        }

        return (
            "You are a precise summarization assistant. "
            "Return output only as JSON matching the provided schema. "
            "Do not return markdown. Do not return prose outside the schema. "
            f"Write all fields in {language_map[request.target_language]}. "
            f"{style_map[request.style]} "
            f"Generate no more than {request.max_bullets} bullets. "
            "Risks and action_items may be empty arrays when not applicable."
        )