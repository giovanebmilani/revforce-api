from app.config.database import get_db
from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.event import Event
from fastapi import Depends

class EventRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def list(self, chart_id: str) -> list[Event]:
        result = await self.__session.execute(
            select(Event).where(Event.chart_id == chart_id)
        )

        return list(result.unique().scalars().all())
    
    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)