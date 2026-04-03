from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_chat_service
from app.main import app
from app.schemas.chat import ChatRequest, ChatResponse, UsageInfo


class FakeChatService:
    async def generate_chat_response(self, request: ChatRequest) -> ChatResponse:
        return ChatResponse(
            content="Hello from fake service",
            model="gpt-4.1-mini",
            provider="openai",
            request_id="req_test_123",
            usage=UsageInfo(
                input_tokens=10,
                output_tokens=20,
                total_tokens=30,
            ),
        )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    def override_get_chat_service() -> FakeChatService:
        return FakeChatService()

    app.dependency_overrides[get_chat_service] = override_get_chat_service
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


def test_chat_endpoint_returns_expected_response(client: TestClient) -> None:
    payload = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "temperature": 0.2,
        "max_output_tokens": 100,
    }

    response = client.post("/api/v1/chat", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "content": "Hello from fake service",
        "model": "gpt-4.1-mini",
        "provider": "openai",
        "request_id": "req_test_123",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20,
            "total_tokens": 30,
        },
    }


def test_chat_endpoint_returns_422_when_messages_empty(client: TestClient) -> None:
    payload = {
        "messages": [],
        "temperature": 0.2,
        "max_output_tokens": 100,
    }

    response = client.post("/api/v1/chat", json=payload)

    assert response.status_code == 422


def test_chat_endpoint_returns_422_when_content_is_blank(client: TestClient) -> None:
    payload = {
        "messages": [
            {"role": "user", "content": "   "}
        ]
    }

    response = client.post("/api/v1/chat", json=payload)

    assert response.status_code == 422


def test_chat_endpoint_returns_422_when_role_is_invalid(client: TestClient) -> None:
    payload = {
        "messages": [
            {"role": "admin", "content": "Hello"}
        ]
    }

    response = client.post("/api/v1/chat", json=payload)

    assert response.status_code == 422