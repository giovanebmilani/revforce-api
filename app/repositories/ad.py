from fastapi import Depends
from uuid import uuid4
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,insert
from sqlalchemy.exc import SQLAlchemyError

from app.config.database import get_db

from app.models.ad import Ad
from app.models.campaign import Campaign
from app.models.account_config import AccountConfig


class AdRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def index(self, account_id: str) -> list[Ad]:
        result = await self.__session.execute(
            select(Ad)
            .join(AccountConfig, AccountConfig.id == Ad.integration_id)
            .where(AccountConfig.account_id == account_id)
        )

        return result.scalars().all()
    
    async def get_or_create(
        self,
        remote_id: str,
        integration_id: str,
        campaign_id: int,
        name: str
    ) -> Ad:
        result = await self.__session.execute(
            select(Ad).where(Ad.remote_id == remote_id)
        )
        ad = result.scalars().first()

        if ad:
            return ad

        ad = Ad(
            remote_id=remote_id,
            integration_id=integration_id,
            campaign_id=campaign_id,
            name=name
        )
        self.__session.add(ad)
        await self.__session.commit()
        await self.__session.refresh(ad)
        return ad

    async def create_or_update(self, data: Ad) -> Ad:
            try:
                stmt = select(Ad).where(
                    (Ad.remote_id == data.remote_id) &
                    (Ad.integration_id == data.integration_id)
                )
                result = await self.__session.execute(stmt)
                instance = result.scalar_one_or_none()

                if instance:
                    instance.updated_at = datetime.utcnow()
                    instance.name = data.name
                    instance.campaign = data.campaign
                    await self.__session.flush()
                    return instance
                else:
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