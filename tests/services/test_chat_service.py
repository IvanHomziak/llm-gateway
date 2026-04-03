import pytest

from app.core.config import Settings
from app.providers.base import ProviderTextResult
from app.schemas.chat import ChatRequest, ChatResponse, UsageInfo
from app.services.chat_service import ChatService


class FakeProvider:
    def __init__(self) -> None:
        self.last_request = None

    async def chat(self, request):
        self.last_request = request
        return ProviderTextResult(
            content="Hello from provider",
            model="gpt-4.1-mini",
            request_id="req_provider_123",
            usage=UsageInfo(
                input_tokens=15,
                output_tokens=25,
                total_tokens=40,
            ),
        )


class EmptyResponseProvider:
    async def chat(self, request):
        return ProviderTextResult(
            content="   ",
            model="gpt-4.1-mini",
            request_id="req_provider_456",
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
async def test_chat_service_maps_provider_result_to_chat_response() -> None:
    settings = build_settings()
    provider = FakeProvider()
    service = ChatService(settings=settings, provider=provider)

    request = ChatRequest(
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.2,
        max_output_tokens=100,
    )

    response = await service.generate_chat_response(request)

    assert isinstance(response, ChatResponse)
    assert response.content == "Hello from provider"
    assert response.model == "gpt-4.1-mini"
    assert response.provider == "openai"
    assert response.request_id == "req_provider_123"
    assert response.usage.input_tokens == 15
    assert response.usage.output_tokens == 25
    assert response.usage.total_tokens == 40


@pytest.mark.asyncio
async def test_chat_service_passes_expected_request_to_provider() -> None:
    settings = build_settings()
    provider = FakeProvider()
    service = ChatService(settings=settings, provider=provider)

    request = ChatRequest(
        messages=[{"role": "user", "content": "Hello"}],
        temperature=0.7,
        max_output_tokens=256,
    )

    await service.generate_chat_response(request)

    assert provider.last_request is not None
    assert provider.last_request.model == "gpt-4.1-mini"
    assert provider.last_request.temperature == 0.7
    assert provider.last_request.max_output_tokens == 256
    assert provider.last_request.messages[0].role == "user"
    assert provider.last_request.messages[0].content == "Hello"


@pytest.mark.asyncio
async def test_chat_service_raises_when_provider_returns_blank_content() -> None:
    settings = build_settings()
    provider = EmptyResponseProvider()
    service = ChatService(settings=settings, provider=provider)

    request = ChatRequest(
        messages=[{"role": "user", "content": "Hello"}]
    )

    with pytest.raises(RuntimeError, match="empty chat content"):
        await service.generate_chat_response(request)