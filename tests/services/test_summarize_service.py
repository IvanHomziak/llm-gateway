import pytest
from pydantic import ValidationError

from app.core.config import Settings
from app.providers.base import ProviderStructuredResult
from app.schemas.chat import UsageInfo
from app.schemas.summarize import SummarizeRequest, SummarizeResponse
from app.services.summarize_service import SummarizeService


class FakeProvider:
    def __init__(self) -> None:
        self.last_request = None

    async def summarize(self, request):
        self.last_request = request
        return ProviderStructuredResult(
            data={
                "title": "Technical Summary",
                "summary": "The system uses a router, service, and provider split.",
                "bullets": [
                    {
                        "text": "Service layer orchestrates the use case.",
                        "importance": "high",
                    },
                    {
                        "text": "Provider layer isolates OpenAI-specific logic.",
                        "importance": "medium",
                    },
                ],
                "risks": ["Timeouts are not handled yet."],
                "action_items": ["Add retry and canonical error mapping."],
            },
            model="gpt-4.1-mini",
            request_id="req_sum_123",
            usage=UsageInfo(
                input_tokens=20,
                output_tokens=40,
                total_tokens=60,
            ),
        )


class MalformedProvider:
    async def summarize(self, request):
        return ProviderStructuredResult(
            data={
                "summary": "Missing title field.",
                "bullets": [],
                "risks": [],
                "action_items": [],
            },
            model="gpt-4.1-mini",
            request_id="req_sum_bad",
            usage=UsageInfo(
                input_tokens=1,
                output_tokens=1,
                total_tokens=2,
            ),
        )


def build_settings() -> Settings:
    return Settings(
        app_name="llm-gateway",
        app_version="0.0.1",
        environment="test",
        log_level="INFO",
        openai_api_key="test-key",
        openai_model_chat="gpt-4.1-mini",
        openai_model_summarize="gpt-4.1-mini",
        openai_provider="openai",
        openai_timeout_total_seconds=30,
        openai_timeout_connect_seconds=2,
        openai_timeout_read_seconds=20,
        openai_timeout_write_seconds=10,
        openai_max_retries=2,
    )


@pytest.mark.asyncio
async def test_summarize_service_maps_provider_result_to_response() -> None:
    settings = build_settings()
    provider = FakeProvider()
    service = SummarizeService(settings=settings, provider=provider)

    request = SummarizeRequest(
        text="The team reviewed llm-gateway architecture.",
        style="technical",
        max_bullets=2,
        target_language="en",
    )

    response = await service.summarize(request)

    assert isinstance(response, SummarizeResponse)
    assert response.title == "Technical Summary"
    assert response.summary == "The system uses a router, service, and provider split."
    assert response.bullets[0].importance == "high"
    assert response.risks == ["Timeouts are not handled yet."]
    assert response.action_items == ["Add retry and canonical error mapping."]


@pytest.mark.asyncio
async def test_summarize_service_passes_expected_request_to_provider() -> None:
    settings = build_settings()
    provider = FakeProvider()
    service = SummarizeService(settings=settings, provider=provider)

    request = SummarizeRequest(
        text="Summarize this architecture note.",
        style="executive",
        max_bullets=3,
        target_language="uk",
    )

    await service.summarize(request)

    assert provider.last_request is not None
    assert provider.last_request.model == "gpt-4.1-mini"
    assert provider.last_request.text == "Summarize this architecture note."
    assert "Ukrainian" in provider.last_request.instructions
    assert "no more than 3 bullets" in provider.last_request.instructions


@pytest.mark.asyncio
async def test_summarize_service_raises_when_provider_returns_invalid_structure() -> None:
    settings = build_settings()
    provider = MalformedProvider()
    service = SummarizeService(settings=settings, provider=provider)

    request = SummarizeRequest(
        text="Valid summarize input.",
        style="executive",
        max_bullets=2,
        target_language="en",
    )

    with pytest.raises(ValidationError):
        await service.summarize(request)
