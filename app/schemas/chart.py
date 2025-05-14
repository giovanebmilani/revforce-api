from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel, Field
from app.models.chart import ChartMetric, ChartSegment, ChartType
from app.models.period import PeriodType
from app.models.chart_source import SourceTable
from app.models.ad_metric import DeviceType
import uuid

class PeriodSchema(BaseModel):
    type: PeriodType
    amount: int

class SourceSchema(BaseModel):
    source_table: SourceTable
    source_id: str

class ChartRequest(BaseModel):
    account_id: str
    name: str = Field(min_length=3)
    position: Optional[int] = None
    type: ChartType
    metric: ChartMetric
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

class CompleteChart(BaseModel):
    id: str
    name: str = Field(min_length=3)
    position: int
    type: ChartType
    metric: ChartMetric
    period: PeriodResponse
    granularity: PeriodResponse
    sources: list[SourceResponse]
    segment: Optional[ChartSegment]

class ChartDataPoint(BaseModel):
    source_id: str
    source_table: SourceTable
    value: int
    date: datetime
    device: DeviceType | None


class ChartResponse(BaseModel):
    chart: CompleteChart
    data: list[ChartDataPoint]


class UpdateChartOrderRequest(BaseModel):
    positions: Dict[str, int]