from fastapi import APIRouter, Depends
from starlette import status
from app.services.charts import ChartService
from app.schemas.chart import ChartRequest

router = APIRouter(
    prefix="/chart",
    tags=["chart"]
)

@router.get("/{chart_id}", status_code=status.HTTP_200_OK)
async def get_chart(chart_id: str, service: ChartService = Depends(ChartService.get_service)):
    return await service.get_chart(chart_id)