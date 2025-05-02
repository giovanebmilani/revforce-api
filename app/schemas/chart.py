from typing import Optional
from pydantic import BaseModel, Field
from app.models.chart import ChartMetric, ChartSegment, ChartType
from app.models.period import PeriodType
from app.models.chart_source import SourceTable
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
    type: ChartType
    metric: ChartMetric
    period: PeriodSchema
    granularity: PeriodSchema
    sources: list[SourceSchema]
    segment: Optional[ChartSegment]
