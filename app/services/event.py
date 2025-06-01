from app.schemas.event import EventResponse
from app.repositories.event import EventRepository
from fastapi import Depends

class EventService():
    def __init__(self, repository: EventRepository):
        self.__repository = repository

    async def list_events(self, id: str) -> list[EventResponse]:
        events = await self.__repository.list(id)

        event_responses = []

        for event in events:
            response = await self._make_event_response(event)
            event_responses.append(response)

        return event_responses
    
    @classmethod
    def get_service(cls, event_repository: EventRepository = Depends(EventRepository.get_service)):
        return cls(event_repository)