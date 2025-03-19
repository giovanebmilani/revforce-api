from fastapi import APIRouter, Depends
from starlette import status

from app.services.insights import InsightsService

router = APIRouter(
    prefix="/insights",
    tags=["insights"]
)


@router.post("", status_code=status.HTTP_200_OK)
async def get_insights(service: InsightsService = Depends(InsightsService.get_service)):
    return await service.get_insights()
