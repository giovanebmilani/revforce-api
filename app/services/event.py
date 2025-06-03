import uuid

from fastapi import Depends, HTTPException
from starlette import status

from app.models.event import Event
from app.repositories.event import EventRepository
from app.schemas.event import EventRequest, EventUpdateRequest
from app.services.charts import ChartService


class EventService:
    def __init__(
            self,
            event_repository: EventRepository,
            chart_service: ChartService,
    ):
        self.__repository = event_repository
        self.__chart_service = chart_service

    async def create_event(self, event_req: EventRequest):
        # this throws 404 if the chart does not exist
        await self.__chart_service.get_chart(event_req.chart_id)

        event = await self.__repository.create(Event(
            id=str(uuid.uuid4()),
            chart_id=event_req.chart_id,
            name=event_req.name,
            description=event_req.description,
            date=event_req.date.replace(tzinfo=None),
            color=event_req.color
        ))

        return event

    async def update_event(self, event_id: str, event_req: EventUpdateRequest):
        event_to_update = await self.__repository.get(event_id)

        if event_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event not found.")

        updated_event = Event(
            id=event_to_update.id,
            chart_id=event_to_update.chart_id,
            name=event_req.name,
            description=event_req.description,
            date=event_req.date.replace(tzinfo=None),
            color=event_req.color
        )

        return await self.__repository.update(event_id, updated_event)

    @classmethod
    async def get_service(
            cls,
            event_repository: EventRepository = Depends(EventRepository.get_service),
            chart_service: ChartService = Depends(ChartService.get_service)
    ):
        return cls(event_repository, chart_service)