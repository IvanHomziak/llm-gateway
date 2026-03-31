from fastapi.testclient import TestClient

from app.main import app
from app.core.config import get_settings

client = TestClient(app)


def test_health_endpoint_returns_expected_schema() -> None:
    settings = get_settings()

    response = client.get("/api/v1/health")
    body = response.json()

    assert response.status_code == 200
    assert body["status"] == "ok"
    assert body["app_name"] == settings.app_name
    assert body["version"] == settings.app_version
    assert body["provider"] == settings.openai_provider