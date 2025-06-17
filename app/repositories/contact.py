from fastapi import Depends
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.config.database import get_db
from app.models.contact import Contact

class ContactRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create(self, contact: Contact) -> Contact:
        insert_stmt = insert(Contact).values(
            id=contact.id,
            integration_id=contact.integration_id,
            remote_id=contact.remote_id,
            email=contact.email,
            first_name=contact.first_name,
            created_at=contact.created_at,
            source=contact.source
        ).on_conflict_do_nothing(index_elements=['remote_id'])

        await self.__session.execute(insert_stmt)
        await self.__session.commit()

        return contact

    async def create_many(self, contacts: list[Contact]) -> list[Contact]:
        for contact in contacts:
            await self.create(contact)

        return contacts

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
