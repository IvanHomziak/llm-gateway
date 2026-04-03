from fastapi import APIRouter, Depends

from app.api.dependencies import get_chat_service
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def create_chat_response(
        request: ChatRequest,
        chat_service: ChatService = Depends(get_chat_service)
) -> ChatResponse:
    return await chat_service.generate_chat_response(request)
