from app.repositories.chart import ChartRepository
from fastapi import Depends, HTTPException
from starlette import status

class ChartService:
    def __init__(self, chart_repository: ChartRepository):
        self.__repository = chart_repository

    async def get_chart(self, chart_id: str):
        chart = await self.__repository.get(chart_id)

        if chart is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found.")
        
        return chart

    @classmethod
    async def get_service(cls, chart_repository: ChartRepository = Depends(ChartRepository.get_service)):
        return cls(chart_repository)