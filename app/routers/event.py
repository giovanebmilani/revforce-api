from starlette import status
from app.schemas.event import EventResponse
from app.services.event import EventService
from fastapi import APIRouter, Depends

router = APIRouter(
    prefix="/event",
    tags=["event"]
)

@router.get("/{chart_id}", status_code=status.HTTP_200_OK, response_model=list[EventResponse])
async def list_chart(chart_id: str, service: EventService = Depends(EventService.get_service)):
    return await service.list_events(chart_id)

@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_event(event_id: str, service: EventService = Depends(EventService.get_service)):
    return await service.delete_event(event_id)

