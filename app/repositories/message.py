import uuid
from sqlalchemy.dialects.postgresql import insert
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app.models.message import Message

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create(self, message: Message) -> Message:
        insert_stmt = insert(Message).values(
            id=message.id,
            integration_id=message.integration_id,
            remote_id=message.remote_id,
            subject=message.subject,
            priority=message.priority,
            create_date=message.create_date
        ).on_conflict_do_nothing(index_elements=['remote_id'])

        await self.__session.execute(insert_stmt)
        
        await self.__session.commit()

        return message
    
    async def create_many(self, messages: list[Message]) -> list[Message]:
        for message in messages:
            await self.create(message)

        return messages

    async def get_or_create(
        self,
        remote_id: str,
        data: dict
    ) -> Message:
        result = await self.__session.execute(
            select(Message).where(Message.remote_id == remote_id)
        )
        message = result.scalars().all()

        if message:
            return message

        message = Message(
            id=str(uuid.uuid4()),
            remote_id=remote_id,
            subject=data.get("subject"),
            priority=data.get("priority"),
            create_date=data.get("cdate")
        )

        self.__session.add(message)
        await self.__session.commit()
        await self.__session.refresh(message)
        return message

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
