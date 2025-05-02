from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from fastapi import Depends

from app.config.database import get_db
from app.models.chart_source import ChartSource

class ChartSourceRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get(self, source_id: str) -> ChartSource | None:
        chart_source = await self.__session.scalar(
            select(ChartSource).where(ChartSource.id == source_id)
        )

        return chart_source

    async def create(self, source: ChartSource) -> ChartSource:
        print('one!!!!')
        result = await self.__session.execute(
            insert(ChartSource)
                .values(
                    id=str(uuid4()),
                    chart_id=source.chart_id,
                    source_id=source.source_id,
                    source_table=source.source_table,
                ).returning(ChartSource)
        )

        print("two")

        chart_source = result.scalar_one()
         
        print("threee")

        await self.__session.commit()

        return chart_source

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)