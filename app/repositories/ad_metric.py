from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.models.ad_metric import AdMetric

class AdMetricRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def save(self, campaign_id: int, metrics: dict) -> AdMetric:
        metric = AdMetric(
            ad_id=metrics.get("ad_id"),
            ctr=metrics.get("ctr"),
            impressions=metrics.get("impressions"),
            views=metrics.get("views"),
            clicks=metrics.get("clicks"),
            device=metrics.get("device"),
            date=metrics.get("date"),
            hour=metrics.get("hour"),
            day=metrics.get("day"),
            month=metrics.get("month"),
            year=metrics.get("year")
        )
        self.__session.add(metric)
        await self.__session.commit()
        await self.__session.refresh(metric)
        return metric

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
