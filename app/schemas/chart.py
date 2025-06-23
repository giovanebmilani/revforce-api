from datetime import datetime
from typing import Optional, Dict

from pydantic import BaseModel, Field

from app.models.ad_metric import DeviceType
from app.models.chart import ChartSegment, ChartType
from app.models.chart_source import ChartMetric
from app.models.chart_source import SourceTable
from app.models.period import PeriodType
from app.schemas.event import EventToAnalyze


class PeriodSchema(BaseModel):
    type: PeriodType
    amount: int


class SourceSchema(BaseModel):
    source_table: SourceTable
    source_id: str
    metrics: list[ChartMetric]


class ChartRequest(BaseModel):
    account_id: str
    name: str = Field(min_length=3)
    position: Optional[int] = None
    type: ChartType
    period: PeriodSchema
    granularity: PeriodSchema
    sources: list[SourceSchema]
    segment: Optional[ChartSegment]


class PeriodResponse(BaseModel):
    type: PeriodType
    amount: int


class SourceResponse(BaseModel):
    id: str
    chart_id: str
    source_table: SourceTable
    source_id: str
    metrics: list[ChartMetric]


class CompleteChart(BaseModel):
    id: str
    name: str = Field(min_length=3)
    position: int
    type: ChartType
    period: PeriodResponse
    granularity: PeriodResponse
    sources: list[SourceSchema]
    segment: Optional[ChartSegment]


class ChartDataPoint(BaseModel):
    source_id: str
    source_table: SourceTable
    value: float
    date: datetime
    metric: ChartMetric
    device: DeviceType | None


class ChartResponse(BaseModel):
    chart: CompleteChart
    data: list[ChartDataPoint]


class UpdateChartOrderRequest(BaseModel):
    positions: Dict[str, int]


class ChartDataPointToAnalyze(BaseModel):
    source_table: SourceTable
    value: int
    date: datetime
    device: Optional[DeviceType]


class ChartToAnalyze(BaseModel):
    name: str
    type: ChartType
    sources: list[SourceSchema]
    period: PeriodResponse
    granularity: PeriodResponse
    segment: Optional[ChartSegment]
    data: list[ChartDataPointToAnalyze]
    events: list[EventToAnalyze]
