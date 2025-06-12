from fastapi import Depends
from uuid import uuid4
from dateutil import parser
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert
from sqlalchemy.exc import SQLAlchemyError

from app.config.database import get_db

from app.models.ad_metric import AdMetric
from app.models.ad import Ad
from app.models.account_config import AccountConfig


class AdMetricRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def index(self, ad_id: str) -> list[Ad]:
        result = await self.__session.execute(
            select(Ad)
            .join(Ad, Ad.id == AdMetric.ad_id)
            .where(AccountConfig.ad_id == ad_id)
        )

        return result.scalars().all()
    
    async def create(self, ad_metric: AdMetric) -> AdMetric:
        await self.__session.execute(
            insert(AdMetric)
                .values(
                    id=str(uuid4()),
                    ad_id=ad_metric.ad_id,
                    ctr=ad_metric.ctr,
                    impressions=ad_metric.impressions,
                    views=ad_metric.views,
                    clicks=ad_metric.clicks,
                    device=ad_metric.device,
                    date=ad_metric.date,
                    hour=ad_metric.hour,
                    day=ad_metric.day,
                    month=ad_metric.month,
                    year=ad_metric.year,
                ).returning(AdMetric)
        )   

        await self.__session.commit()

    async def create_or_update(self, data: AdMetric) -> AdMetric:
        try:
            stmt = select(AdMetric).where(
                (AdMetric.ad_id == data.ad_id) &
                (AdMetric.date == data.date) &
                (AdMetric.device == data.device)
            )
            result = await self.__session.execute(stmt)
            instance = result.scalar_one_or_none()

            if instance:
                instance.updated_at = datetime.now()
                instance.ctr = data.ctr
                instance.impressions = data.impressions
                instance.views = data.views
                instance.device = data.device
                instance.date = data.date
                instance.hour = data.hour
                instance.day = data.day
                instance.month = data.month
                instance.year = data.year
                await self.__session.flush()
                return instance
            else:
                data.updated_at = datetime.now()
                data.id = str(uuid4())
                self.__session.add(data)
                await self.__session.flush()
                return data

        except SQLAlchemyError:
            if self.__session.in_transaction():
                try:
                    await self.__session.rollback()
                except Exception:
                    pass
            raise
        finally:
            if self.__session.in_transaction():
                try:
                    await self.__session.commit()
                except Exception:
                    await self.__session.rollback()
                    raise

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)