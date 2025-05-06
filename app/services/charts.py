from fastapi import Depends, HTTPException
from starlette import status
from asyncio import gather
import uuid

from app.models.chart import Chart
from app.models.period import Period
from app.models.chart_source import ChartSource
from app.schemas.chart import ChartRequest, ChartResponse, UpdateChartOrderRequest

from app.repositories.chart import ChartRepository
from app.repositories.period import PeriodRepository
from app.repositories.chart_source import ChartSourceRepository
from app.services.accounts import AccountService
from app.services.chart_data import DataService


class ChartService:
    def __init__(
        self,
        chart_repository: ChartRepository,
        period_repository: PeriodRepository,
        chart_source_repository: ChartSourceRepository,
        account_service: AccountService,
        data_service: DataService,
    ):
        self.__repository = chart_repository
        self.__period_repo = period_repository
        self.__source_repo = chart_source_repository
        self.__account_serivce = account_service
        self.__data_service = data_service

    async def _make_chart_response(self, chart: Chart) -> ChartResponse:
        data = await self.__data_service.get_for_chart(chart)
        
        return ChartResponse(
            chart={
                **chart.__dict__,
                "period": chart.period.__dict__,
                "granularity": chart.granularity.__dict__,
                "sources":  [s.__dict__ for s in chart.sources]
            },
            data=data,
        )


    async def get_chart(self, chart_id: str) -> ChartResponse:
        chart = await self.__repository.get(chart_id)

        if chart is None: 
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found.")

        return await self._make_chart_response(chart)
    
    async def list_charts(self, account_id: str) -> list[ChartResponse]:
        charts = await self.__repository.list(account_id)

        tasks = [self._make_chart_response(chart) for chart in charts]

        chart_responses = await gather(*tasks)

        return chart_responses
    
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
            period_id=period.id,
            granularity_id=granularity.id,
            segment=chart_req.segment,
        ))

        for source in chart_req.sources:
            await self.__source_repo.create(ChartSource(
                chart_id=chart.id,
                source_id=source.source_id,
                source_table=source.source_table,
            ))

        return chart

    async def delete_chart(self, chart_id: str):
        await self.__repository.delete(chart_id)

    async def update_chart(self, chart_id: str, chart_req: ChartRequest):
        chart_to_update = await self.__repository.get(chart_id)

        if chart_to_update is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found.")

        period = await self.__period_repo.update(chart_to_update.period_id, Period(
            type=chart_req.period.type,
            amount=chart_req.period.amount,
        ))

        granularity = await self.__period_repo.update(chart_to_update.granularity_id, Period(
            type=chart_req.granularity.type,
            amount=chart_req.granularity.amount,
        ))

        updated_chart = Chart(
            id=chart_to_update.id,
            account_id=chart_to_update.account_id, # don't change the account id
            name=chart_req.name,
            type=chart_req.type,
            metric=chart_req.metric,
            period_id=period.id,
            granularity_id=granularity.id,
            segment=chart_req.segment,
        )

        chart = await self.__repository.update(updated_chart)

        await self.__source_repo.delete_by_chart_id(chart_id)

        for source in chart_req.sources:
            await self.__source_repo.create(ChartSource(
                chart_id=chart_id,
                source_id=source.source_id,
                source_table=source.source_table,
            ))

        return chart

    async def update_order(self, new_order: UpdateChartOrderRequest):
        for id, pos in new_order.positions.items():
            positions = await self.__repository.update_order(id, pos)

        return positions

    @classmethod
    async def get_service(
        cls,
        chart_repository: ChartRepository = Depends(ChartRepository.get_service),
        period_repository: PeriodRepository = Depends(PeriodRepository.get_service),
        chart_source_repository: ChartSourceRepository = Depends(ChartSourceRepository.get_service),
        account_service: AccountService = Depends(AccountService.get_service),
        data_service: DataService = Depends(DataService.get_service)
    ):
        return cls(chart_repository, period_repository, chart_source_repository, account_service, data_service)
