from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.config.database import get_db
from app.models.contact import Contact

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_or_create(
        self,
        remote_id: str,
        email: str,
        first_name: str,
        created_at: str | datetime,
        source: str
    ) -> Contact:
        result = await self.__session.execute(
            select(Contact).where(Contact.remote_id == remote_id)
        )
        contact = result.scalars().first()

        if isinstance(created_at, str):
            try:
                created_at = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                created_at = datetime.fromisoformat(created_at)

        if contact:
            return contact

        contact = Contact(
            id=remote_id,
            remote_id=remote_id,
            email=email,
            first_name=first_name,
            created_at=created_at,
            source=source
        )

        self.__session.add(contact)
        await self.__session.commit()
        await self.__session.refresh(contact)
        return contact

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
