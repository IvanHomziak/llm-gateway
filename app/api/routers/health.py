from fastapi import APIRouter
from fastapi.params import Depends

from app.core.config import Settings, get_settings

from app.schemas.health import HealthResponse

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/", response_model=HealthResponse, status_code=200)
async def health(settings: Settings = Depends(get_settings)) -> HealthResponse:
    model = HealthResponse(
        status="ok",
        app_name=settings.app_name,
        version=settings.app_version,
        provider=settings.openai_provider
    )

    return model




