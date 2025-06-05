from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app.models.message import Message

class MessageRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_or_create(
        self,
        remote_id: str,
        data: dict
    ) -> Message:
        result = await self.__session.execute(
            select(Message).where(Message.remote_id == remote_id)
        )
        message = result.scalars().first()

        if message:
            return message

        message = Message(
            remote_id=remote_id,
            contact_id=data.get("contact_id"),
            type=data.get("activity_type"),
            campaign_id=data.get("campaign_id"),
            message_id=data.get("message_id"),
            timestamp=data.get("timestamp")
        )

        self.__session.add(message)
        await self.__session.commit()
        await self.__session.refresh(message)
        return message

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
