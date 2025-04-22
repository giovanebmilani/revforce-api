from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.chart import Chart


class ChartRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_all(self) -> list[Chart]:
        result = await self.__session.execute(
            select(Chart)
        )

        return list(result.scalars().all())

    async def get(self, id: str) -> Chart | None:
        result = await self.__session.execute(
            select(Chart).where(Chart.id == id)
        )

        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Chart | None:
        result = await self.__session.execute(
            select(Chart).where(Chart.name == name)
        )

        return result.scalar_one_or_none()
    
    

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
