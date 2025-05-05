from uuid import uuid4
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.config.database import get_db

from app.models.account_config import AccountConfig


class AccountConfigRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def index(self) -> list[AccountConfig]:
        result = await self.__session.execute(
            select(AccountConfig)
        )

        return result.scalars().all()

    async def get(self, id: str) -> AccountConfig | None:
        result = await self.__session.execute(
            select(AccountConfig).where(AccountConfig.id == id)
        )

        return result.scalar_one_or_none()

    async def get_by_account_id(self, account_id: str) -> list[AccountConfig]:
        result = await self.__session.execute(
            select(AccountConfig).where(AccountConfig.account_id == account_id)
        )

        return result.scalars().all()

    async def create(self, account_config: AccountConfig) -> AccountConfig:
        result = await self.__session.execute(
            insert(AccountConfig)
                .values(
                    id=str(uuid4()),
                    account_id=account_config.account_id,
                    type=account_config.type,
                    api_secret=account_config.api_secret,
                )
                .returning(AccountConfig)
        )

        await self.__session.commit()

        return result.scalar_one()

    async def update(self, id: str, account_config: AccountConfig) -> AccountConfig | None:
        result = await self.__session.execute(
            update(AccountConfig)
                .where(AccountConfig.id == id)
                .values(
                    account_id=account_config.account_id,
                    type=account_config.type,
                    api_secret=account_config.api_secret,
                )
                .returning(AccountConfig)
        )

        await self.__session.commit()

        return result.scalar_one_or_none() 

    async def delete(self, id: str) -> AccountConfig:
        result = await self.__session.execute(
            delete(AccountConfig)
                .where(AccountConfig.id == id)
                .returning(AccountConfig)
        )

        await self.__session.commit()

        return result.scalar_one_or_none()

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)