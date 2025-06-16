from datetime import datetime
from fastapi import Depends
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

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
    
    async def get_or_create(
        self,
        remote_id: str,
        name: str,
        start_date_raw: str | datetime | None,
        integration_id: str
    ) -> Campaign:
        result = await self.__session.execute(
            select(Campaign).where(Campaign.remote_id == remote_id)
        )
        campaign = result.scalars().first()

        if campaign:
            return campaign

        start_date = None
        if isinstance(start_date_raw, datetime):
            start_date = start_date_raw
        elif isinstance(start_date_raw, str):
            try:
                if "Z" in start_date_raw:
                    start_date_raw = start_date_raw.replace("Z", "+00:00")
                start_date = datetime.fromisoformat(start_date_raw)
            except ValueError:
                print(f"Formato de data inválido: {start_date_raw}")
        else:
            print(f"Tipo de start_date_raw inválido: {type(start_date_raw)}")

        if not start_date:
            raise ValueError(f"Campanha {remote_id} sem start_date válido")

        if start_date.tzinfo is not None:
            start_date = start_date.replace(tzinfo=None)

        campaign = Campaign(
            id=remote_id,
            remote_id=remote_id,
            integration_id=integration_id,
            name=name,
            start_date=start_date,
            end_date=None,
            daily_budget=None,
            monthly_budget=None
        )

        self.__session.add(campaign)
        await self.__session.commit()
        await self.__session.refresh(campaign)
        return campaign

    async def create_or_update(self, data: Campaign) -> Campaign:
        try:
            stmt = select(Campaign).where(
                (Campaign.remote_id == data.remote_id) &
                (Campaign.integration_id == data.integration_id)
            )
            result = await self.__session.execute(stmt)
            instance = result.scalar_one_or_none()

            if instance:
                instance.updated_at = datetime.now()
                instance.name = data.name
                instance.start_date = data.start_date
                instance.end_date = data.end_date
                instance.daily_budget = data.daily_budget
                instance.monthly_budget = data.monthly_budget
                await self.__session.flush()
                return instance
            else:
                data.id = str(uuid4())
                data.created_at = datetime.utcnow()
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