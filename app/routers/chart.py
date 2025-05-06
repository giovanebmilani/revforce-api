from fastapi import APIRouter, Depends
from starlette import status
from app.services.charts import ChartService
from app.schemas.chart import ChartRequest, ChartResponse, UpdateChartOrderRequest

router = APIRouter(
    prefix="/chart",
    tags=["chart"]
)

@router.get("/{chart_id}", status_code=status.HTTP_200_OK, response_model=ChartResponse)
async def get_chart(chart_id: str, service: ChartService = Depends(ChartService.get_service)):
    return await service.get_chart(chart_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_chart(chart: ChartRequest, service: ChartService = Depends(ChartService.get_service)):
    return await service.create_chart(chart)

@router.get("/{account_id}/all", status_code=status.HTTP_200_OK, response_model=list[ChartResponse])
async def list_chart(account_id: str, service: ChartService = Depends(ChartService.get_service)):
    return await service.list_charts(account_id)

@router.delete("/{chart_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chart(chart_id: str, service: ChartService = Depends(ChartService.get_service)):
    return await service.delete_chart(chart_id)

@router.put("/{chart_id}", status_code=status.HTTP_201_CREATED)
async def update_chart(chart_id: str, chart: ChartRequest, service: ChartService = Depends(ChartService.get_service)):
    return await service.update_chart(chart_id, chart)

@router.put("/order", status_code=status.HTTP_200_OK0)
async def update_order(body: UpdateChartOrderRequest, service: ChartService = Depends(ChartService.get_service)):
    return await service.update_order(body)