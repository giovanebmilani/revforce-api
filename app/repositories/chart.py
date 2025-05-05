from fastapi import Depends
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import uuid4

from app.config.database import get_db
from app.models.chart import Chart

class ChartRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def list(self, account_id: str) -> list[Chart]:
        result = await self.__session.execute(
            select(Chart).where(Chart.account_id == account_id)
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
    
    async def create(self, chart: Chart) -> Chart:
        result = await self.__session.execute(
            insert(Chart)
                .values(
                    name=chart.name,
                    id=str(uuid4()),
                    account_id=chart.account_id,
                    type=chart.type,
                    metric=chart.metric,
                    period_id=chart.period_id,
                    granularity_id=chart.granularity_id,
                    segment=chart.segment
                ).returning(Chart)
        )

        await self.__session.commit()

        return result.scalar_one()
    
    async def delete(self, id: str) -> Chart:
        chart = await self.get(id)

        # Para o cascade funcionar, é preciso utilizar o delete pelo ORM
        # https://docs.sqlalchemy.org/en/20/orm/queryguide/dml.html#orm-queryguide-update-delete-caveats
        await self.__session.delete(chart)

        await self.__session.commit()

        return chart

    async def update(self, chart: Chart) -> Chart:
        result = await self.__session.execute(
            update(Chart)
                .where(Chart.id == chart.id)
                .values(
                    name=chart.name,
                    type=chart.type,
                    metric=chart.metric,
                    period=chart.period,
                    granularity=chart.granularity,
                    segment=chart.segment
                ).returning(Chart)
        )

        await self.__session.commit()

        return result.scalar_one()

    async def update(self, chart: Chart) -> Chart:
        result = await self.__session.execute(
            update(Chart)
                .where(Chart.id == chart.id)
                .values(
                    name=chart.name,
                    type=chart.type,
                    metric=chart.metric,
                    period=chart.period,
                    granularity=chart.granularity,
                    segment=chart.segment
                ).returning(Chart)
        )

        await self.__session.commit()

        return result.scalar_one()

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
