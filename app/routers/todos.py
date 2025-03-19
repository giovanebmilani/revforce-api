from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.todos import TodoRequest
from app.services.todos import TodosService

router = APIRouter(
    prefix="/todos",
    tags=["todos"]
)


@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def get_todo(todo_id: int, service: TodosService = Depends(TodosService.get_service)):
    return await service.get_todo(todo_id)


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_todo(todo_request: TodoRequest, service: TodosService = Depends(TodosService.get_service)):
    return await service.create_todo(todo_request)
