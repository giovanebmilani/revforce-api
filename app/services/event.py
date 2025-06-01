from app.schemas.event import EventResponse

class EventService():
# adicionar construtor 
    async def list_event(self, id: str) -> list[EventResponse]:
        events = await self.__repository.list(id)

        event_responses = []

        for event in events:
            response = await self._make_event_response(event)
            event_responses.append(response)

        return event_responses
    
# get_service

