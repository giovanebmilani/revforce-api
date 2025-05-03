from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, delete, update
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
        result = await self.__session.execute(
            insert(ChartSource)
                .values(
                    id=str(uuid4()),
                    chart_id=source.chart_id,
                    source_id=source.source_id,
                    source_table=source.source_table,
                ).returning(ChartSource)
        )

        chart_source = result.scalar_one()
         
        await self.__session.commit()

        return chart_source

    async def update(self, source: ChartSource) -> ChartSource:
        result = await self.__session.execute(
            update(ChartSource)
            .where(ChartSource.id == source.id)
            .values(
                chart_id=source.chart_id,
                source_id=source.source_id,
                source_table=source.source_table,
            )
            .returning(ChartSource)
        )

        updated_source = result.scalar_one_or_none()
        await self.__session.commit()

        return updated_source

    async def delete_by_chart_id(self, chart_id: str):
        await self.__session.execute(
            delete(ChartSource).where(ChartSource.chart_id == chart_id)
        )
        await self.__session.commit()

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)