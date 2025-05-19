import math
from fastapi import Depends
from asyncio import gather
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from datetime import datetime, timedelta
from collections import defaultdict

from app.config.database import get_db

from app.schemas.chart import ChartDataPoint, PeriodSchema

from app.models.chart import ChartSegment, Chart
from app.models.ad import Ad
from app.models.ad_metric import AdMetric, DeviceType
from app.models.chart_source import ChartMetric, SourceTable
from app.models.period import PeriodType

def timedelta_from_period(period: PeriodSchema) -> timedelta:
    match period.type:
        case PeriodType.month: return timedelta(days=30 * period.amount)
        case PeriodType.week: return timedelta(weeks=period.amount)
        case PeriodType.day: return timedelta(days=period.amount)
        case PeriodType.hour: return timedelta(hours=period.amount)
        case _: raise NotImplementedError(f"Unsupported period type: {period.type}")

def group_by_date(
    data_points: list[ChartDataPoint],
    period: PeriodSchema
) -> list[ChartDataPoint]:
    step_seconds = timedelta_from_period(period).total_seconds()

    grouped: list[ChartDataPoint] = []

    for dp in data_points:
        timestamp = dp.date.timestamp()
        floored_timestamp = math.floor(timestamp / step_seconds) * step_seconds
        floored_datetime = datetime.fromtimestamp(floored_timestamp, tz=dp.date.tzinfo)
        grouped.append(dp.model_copy(update={ "date": floored_datetime }))

    return grouped

def group_by_device(data_points: list[ChartDataPoint]) -> list[ChartDataPoint]:
    return [dp.model_copy(update={ "device": None }) for dp in data_points]


def aggregate_data_points(dps: list[ChartDataPoint]) -> list[ChartDataPoint]: 
    # source, source id, date, device
    dd: defaultdict[(SourceTable, str, datetime, DeviceType, ChartMetric), int] = defaultdict(int)

    for dp in dps:
        dd[(dp.source_table, dp.source_id, dp.date, dp.device, dp.metric)] += dp.value

    final = []

    for (source_table, source_id, date, device, metric), value in dd.items():
        final.append(ChartDataPoint(
            source_table=source_table,
            source_id=source_id,
            date=date,
            device=device,
            value=value,
            metric=metric
        ))

    return final

class DataService:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_for_source_and_metric(
        self, 
        *,
        source_table: SourceTable, 
        source_id: str, 
        period: PeriodSchema,
        granularity: PeriodSchema,
        metric: ChartMetric,
        segment: ChartSegment,
        **_
    ) -> list[ChartDataPoint]:
        # create a variable `value_field` to get the right metric as the value
        match metric:
            case ChartMetric.click: value_field = AdMetric.clicks.label("value")
            case ChartMetric.ctr: value_field = AdMetric.ctr.label("value")
            case ChartMetric.impression: value_field = AdMetric.impressions.label("value")
            case ChartMetric.spend: value_field = AdMetric.spend.label("value")
            case _: raise ValueError(f"Unsupported metric: {metric}")

        match source_table:
            case SourceTable.campaign:
                time_query = select(AdMetric.date).join(Ad).where(Ad.campaign_id == source_id)
                data_query = (select(AdMetric, value_field)
                    .join(Ad)
                    .where(Ad.campaign_id == source_id)
                )

            case SourceTable.ad:
                time_query = select(AdMetric.date).where(AdMetric.ad_id == source_id)
                data_query = (
                    select(AdMetric, value_field)
                    .where(AdMetric.ad_id == source_id)
                )

        start_time = await self.__session.scalar(
            time_query.order_by(desc(AdMetric.date)).limit(1)
        )

        # there are no metrics for the given source
        if start_time is None:
            return []

        start_time -= timedelta_from_period(period)

        # here we can't use __session.scalars because we can't
        raw_data = await self.__session.execute(
            data_query.where(AdMetric.date > start_time)
        )

        dps = [ChartDataPoint(
                    date=d.date,
                    device=d.device,
                    source_id=source_id,
                    source_table=source_table,
                    value=value,
                    metric=metric,
            ) for (d, value) in raw_data.all()]


        grouped = group_by_date(dps, granularity)

        # if we don't care about the device, set everything to device None
        if segment != ChartSegment.device:
            grouped = group_by_device(grouped)

        # more grouping logic goes here


        aggregated = aggregate_data_points(grouped)

        return aggregated

    async def get_for_source(self, **kwargs) -> list[ChartDataPoint]:
        data: list[ChartDataPoint] = []
        for metric in kwargs['metrics']:
            data.extend(await self.get_for_source_and_metric(**kwargs, metric=metric))

        return data


    async def get_for_chart(self, chart: Chart) -> list[ChartDataPoint]:
        tasks = []
        for source in chart.sources:
            tasks.append(self.get_for_source(
                source_id=source.source_id,
                source_table=source.source_table,
                period=chart.period,
                granularity=chart.granularity,
                metrics=source.metrics,
                segment=chart.segment,
            ))

        results = await gather(*tasks)

        return [data_point for result in results for data_point in result]


    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        return cls(db)