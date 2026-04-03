from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_summarize_service
from app.main import app
from app.schemas.summarize import SummarizeRequest, SummarizeResponse


class FakeSummarizeService:
    async def summarize(self, request: SummarizeRequest) -> SummarizeResponse:
        return SummarizeResponse(
            title="Architecture Discussion Summary",
            summary="The team discussed service boundaries and structured outputs.",
            bullets=[
                {
                    "text": "A dedicated provider adapter is needed.",
                    "importance": "high",
                },
                {
                    "text": "Summarize output must remain machine-readable.",
                    "importance": "medium",
                },
            ],
            risks=["Timeout policy is not implemented yet."],
            action_items=["Add tracing for summarize flow."],
        )


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    def override_get_summarize_service() -> FakeSummarizeService:
        return FakeSummarizeService()

    app.dependency_overrides[get_summarize_service] = override_get_summarize_service
    test_client = TestClient(app)

    yield test_client

    app.dependency_overrides.clear()


def test_summarize_endpoint_returns_expected_response(client: TestClient) -> None:
    payload = {
        "text": "The team reviewed the architecture for llm-gateway.",
        "style": "executive",
        "max_bullets": 2,
        "target_language": "en",
    }

    response = client.post("/api/v1/summarize", json=payload)

    assert response.status_code == 200
    assert response.json() == {
        "title": "Architecture Discussion Summary",
        "summary": "The team discussed service boundaries and structured outputs.",
        "bullets": [
            {
                "text": "A dedicated provider adapter is needed.",
                "importance": "high",
            },
            {
                "text": "Summarize output must remain machine-readable.",
                "importance": "medium",
            },
        ],
        "risks": ["Timeout policy is not implemented yet."],
        "action_items": ["Add tracing for summarize flow."],
    }


def test_summarize_endpoint_returns_422_when_text_is_blank(
        client: TestClient,
) -> None:
    payload = {
        "text": "   ",
        "style": "executive",
        "max_bullets": 2,
        "target_language": "en",
    }

    response = client.post("/api/v1/summarize", json=payload)

    assert response.status_code == 422


def test_summarize_endpoint_returns_422_when_style_is_invalid(
        client: TestClient,
) -> None:
    payload = {
        "text": "Some valid text.",
        "style": "marketing",
        "max_bullets": 2,
        "target_language": "en",
    }

    response = client.post("/api/v1/summarize", json=payload)

    assert response.status_code == 422


def test_summarize_endpoint_returns_422_when_max_bullets_out_of_range(
        client: TestClient,
) -> None:
    payload = {
        "text": "Some valid text.",
        "style": "executive",
        "max_bullets": 0,
        "target_language": "en",
    }

    response = client.post("/api/v1/summarize", json=payload)

    assert response.status_code == 422
