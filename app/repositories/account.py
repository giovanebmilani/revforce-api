from uuid import uuid4
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.config.database import get_db

from app.models.account import Account


class AccountRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def index(self) -> list[Account]:
        result = await self.__session.execute(
            select(Account)
        )

        return result.scalars().all()

    async def get(self, id: str) -> Account | None:
        result = await self.__session.execute(
            select(Account).where(Account.id == id)
        )

        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Account | None:
        result = await self.__session.execute(
            select(Account).where(Account.name == name)
        )

        return result.scalar_one_or_none()

    async def create(self, name: str) -> Account:
        result = await self.__session.execute(
            insert(Account)
                .values(name=name, id=str(uuid4()))
                .returning(Account)
        )

        await self.__session.commit()

        return result.scalar_one()

    async def update(self, id: str, account: Account) -> Account | None:
        result = await self.__session.execute(
            update(Account)
                .where(Account.id == id)
                .values(name=account.name)
                .returning(Account)
        )

        await self.__session.commit()

        return result.scalar_one_or_none() 

    async def delete(self, id: str) -> Account:
        result = await self.__session.execute(
            delete(Account)
                .where(Account.id == id)
                .returning(Account)
        )

        await self.__session.commit()

        return result.scalar_one_or_none()


    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)