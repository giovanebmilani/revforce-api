from fastapi import APIRouter, Depends
from starlette import status

from app.schemas.event import EventRequest, EventUpdateRequest
from app.services.event import EventService

router = APIRouter(
    prefix="/event",
    tags=["event"]
)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_event(event: EventRequest, service: EventService = Depends(EventService.get_service)):
    return await service.create_event(event)

@router.put("/{event_id}", status_code=status.HTTP_201_CREATED)
async def update_event(event_id: str, event: EventUpdateRequest, service: EventService = Depends(EventService.get_service)):
    return await service.update_event(event_id, event)

