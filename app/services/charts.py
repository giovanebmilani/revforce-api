from fastapi import Depends, HTTPException
from starlette import status
import uuid

from app.models.chart import Chart
from app.models.period import Period
from app.models.chart_source import ChartSource
from app.schemas.chart import ChartRequest
from app.repositories.chart import ChartRepository
from app.repositories.period import PeriodRepository
from app.repositories.chart_source import ChartSourceRepository
from app.services.accounts import AccountService

class ChartService:
    def __init__(
        self,
        chart_repository: ChartRepository,
        period_repository: PeriodRepository,
        chart_source_repository: ChartSourceRepository,
        account_service: AccountService
    ):
        self.__repository = chart_repository
        self.__period_repo = period_repository
        self.__source_repo = chart_source_repository
        self.__account_serivce = account_service

    async def get_chart(self, chart_id: str):
        chart = await self.__repository.get(chart_id)

        if chart is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found.")
        
        return chart
    
    async def list_chart(self, account_id: str):
        charts = await self.__repository.list(account_id)
        
        return charts
    
    async def create_chart(self, chart_req: ChartRequest):
        # this throws 404 if the account does not exist
        await self.__account_serivce.get_account(chart_req.account_id)

        chart_same_name = await self.__repository.get_by_name(chart_req.name)

        if chart_same_name is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Chart with name already exists")

        period = await self.__period_repo.create(Period(
            id=str(uuid.uuid4()),
            type=chart_req.period.type,
            amount=chart_req.period.amount,
        ))

        granularity = await self.__period_repo.create(Period(
            id=str(uuid.uuid4()),
            type=chart_req.granularity.type,
            amount=chart_req.granularity.amount,
        ))
        
        chart = await self.__repository.create(Chart(
            id=str(uuid.uuid4()),
            account_id=chart_req.account_id,
            name=chart_req.name,
            type=chart_req.type,
            metric=chart_req.metric,
            period=period.id,
            granularity=granularity.id,
            segment=chart_req.segment,
        ))

        print(chart.id)

        for source in chart_req.sources:
            await self.__source_repo.create(ChartSource(
                chart_id=chart.id,
                source_id=source.source_id,
                source_table=source.source_table,
            ))

        return chart

    @classmethod
    async def get_service(
        cls,
        chart_repository: ChartRepository = Depends(ChartRepository.get_service),
        period_repository: PeriodRepository = Depends(PeriodRepository.get_service),
        chart_source_repository: ChartSourceRepository = Depends(ChartSourceRepository.get_service),
        account_service: AccountService = Depends(AccountService.get_service)
    ):
        return cls(chart_repository, period_repository, chart_source_repository, account_service)
