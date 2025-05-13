from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config.database import get_db

from app.models.campaign import Campaign
from app.models.account_config import AccountConfig


class CampaignRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def index(self, account_id: str) -> list[Campaign]:
        result = await self.__session.execute(
            select(Campaign)
            .join(AccountConfig, AccountConfig.id == Campaign.integration_id)
            .where(AccountConfig.account_id == account_id)
        )

        return result.scalars().all()

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)