from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.chat import ChatRequest, ChatResponse, History
from app.services.chat import ChatService

router = APIRouter(
    prefix="/chat",
    tags=["chat"]
)


@router.post("/", status_code=status.HTTP_200_OK, response_model=ChatResponse)
async def chat(chat_data: ChatRequest, service: ChatService = Depends(ChatService.get_service)):
    return await service.chat(chat_data)

@router.post("/assistant", response_model=ChatResponse)
async def chat_assistant(chat_data: ChatRequest, service: ChatService = Depends(ChatService.get_service)):
    return await service.chat_assistant(chat_data)
