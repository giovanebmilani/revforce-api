from fastapi import Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.config.database import get_db
from app.schemas.todos import TodoRequest
from app.models.todos import Todos


class TodosService:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_todo(self, todo_id: int):
        result = await self.__session.execute(
            select(Todos).where(Todos.id == todo_id)
        )

        todo = result.scalar_one_or_none()

        if todo is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Todo not found.")

        return todo

    async def create_todo(self, todo_request: TodoRequest):
        result = await self.__session.execute(
            insert(Todos)
                .values(todo_request.model_dump())
                .returning(Todos.id)
        )

        await self.__session.commit()

        return result.scalar_one()  # gets the inserted item's ID

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        """ Dependency to inject the service into routes """
        return cls(db)
