from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

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

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)