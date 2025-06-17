from fastapi import Depends
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import get_db
from app.models.deal import Deal

class DealRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def create(self, deal: Deal) -> Deal:
        insert_stmt = insert(Deal).values(
            id=deal.id,
            remote_id=deal.remote_id,
            contact_id=deal.contact_id,
            integration_id=deal.integration_id,
            title=deal.title,
            status=deal.status,
            value=deal.value,
            currency=deal.currency,
            created_at=deal.created_at,
            closed_at=deal.closed_at
        ).on_conflict_do_nothing(index_elements=['remote_id'])

        await self.__session.execute(insert_stmt)
        await self.__session.commit()

        return deal
    
    async def create_many(self, deals: list[Deal]) -> list[Deal]:
        for deal in deals:
            await self.create(deal)
        
        return deals

    async def get_or_create(
        self,
        remote_id: str,
        data: dict
    ) -> Deal:
        result = await self.__session.execute(
            select(Deal).where(Deal.remote_id == remote_id)
        )
        deal = result.scalars().first()

        if deal:
            return deal

        deal = Deal(
            id=remote_id,
            remote_id=remote_id,
            contact_id=data.get("contact", ""),
            account_id=None, 
            title=data.get("title", ""),
            status=data.get("status", ""),
            value=float(data.get("value", 0)),
            currency=data.get("currency", "USD"),
            created_at=data.get("created_timestamp"),
            closed_at=data.get("close_date")
        )

        self.__session.add(deal)
        await self.__session.commit()
        await self.__session.refresh(deal)
        return deal

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)
