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

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_chart(chart: ChartRequest, service: ChartService = Depends(ChartService.get_service)):
    return await service.create_chart(chart)

@router.get("/{account_id}/all", status_code=status.HTTP_200_OK)
async def list_chart(account_id: str, service: ChartService = Depends(ChartService.get_service)):
    return await service.list_chart(account_id)
