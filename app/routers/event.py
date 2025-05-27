from starlette import status
from app.schemas.event import EventRequest, EventResponse, EventUpdateRequest
from app.services.event import EventService
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/event",
    tags=["event"]
)

@router.get("/{chart_id}", status_code=status.HTTP_200_OK, response_model=list[EventResponse])
async def list_chart(chart_id: str, service: EventService = Depends(EventService.get_service)):
    return await service.list_events(chart_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventRequest, service: EventService = Depends(EventService.get_service)):
    return await service.create_event(event)

@router.put("/{event_id}", status_code=status.HTTP_200_OK)
async def update_event(event_id: str, event: EventUpdateRequest, service: EventService = Depends(EventService.get_service)):
    return await service.update_event(event_id, event)

