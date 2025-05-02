from uuid import uuid4
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete

from app.config.database import get_db

from app.models.period import Period


class PeriodRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def index(self) -> list[Period]:
        result = await self.__session.execute(
            select(Period)
        )

        return list(result.scalars().all())

    async def get(self, id: str) -> Period | None:
        result = await self.__session.execute(
            select(Period).where(Period.id == id)
        )

        return result.scalar_one_or_none()


    async def create(self, period: Period) -> Period:
        result = await self.__session.execute(
            insert(Period)
                .values(id=str(uuid4()), type=period.type, amount=period.amount)
                .returning(Period)
        )

        await self.__session.commit()

        return result.scalar_one()


    async def update(self, id: str, period: Period) -> Period | None:
        result = await self.__session.execute(
            update(Period)
                .where(Period.id == id)
                .values(id=str(uuid4()), type=period.type, amount=period.amount)
                .returning(Period)
        )

        await self.__session.commit()

        return result.scalar_one_or_none() 

    async def delete(self, id: str) -> Period:
        result = await self.__session.execute(
            delete(Period)
                .where(Period.id == id)
                .returning(Period)
        )

        await self.__session.commit()

        return result.scalar_one_or_none()


    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)