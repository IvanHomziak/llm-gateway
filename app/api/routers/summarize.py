from fastapi import APIRouter, Depends

from app.api.dependencies import get_summarize_service
from app.schemas.summarize import SummarizeRequest, SummarizeResponse
from app.services.summarize_service import SummarizeService

router = APIRouter(prefix="/summarize", tags=["Summarize"])


@router.post("", response_model=SummarizeResponse)
async def create_summary(
        request: SummarizeRequest,
        summarize_service: SummarizeService = Depends(get_summarize_service),
) -> SummarizeResponse:
    return await summarize_service.summarize(request)
