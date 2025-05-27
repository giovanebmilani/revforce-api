from sqlalchemy import select 
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.chart import Event

class EventRepository:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def list(self, chart_id: str) -> list[Event]:
        result = await self.__session.execute(
            select(Event).where(Event.chart_id == chart_id)
        )

        return list(result.unique().scalars().all())
    
