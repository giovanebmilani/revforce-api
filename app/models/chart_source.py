from typing import TYPE_CHECKING, List 
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum, ARRAY
import enum

if TYPE_CHECKING:
    from .chart import Chart

from app.config.database import Base

class SourceTable(str, enum.Enum):
    campaign = 'campaign'
    ad = 'ad'
    crm = 'crm'

class ChartMetric(str, enum.Enum):
    ctr = 'ctr'
    click = 'click'
    impression = 'impression'
    spend = 'spend'

class ChartSource(Base):
    __tablename__ = "chart_sources"

    id: Mapped[str] = mapped_column(primary_key=True)
    chart_id: Mapped[str] = mapped_column(ForeignKey("charts.id"))
    source_id: Mapped[str]
    source_table: Mapped[SourceTable] = mapped_column(Enum(SourceTable))
    metrics: Mapped[List[ChartMetric]] = mapped_column(ARRAY(Enum(ChartMetric)), nullable=True)

    # Relacionamento com Chart
    chart: Mapped["Chart"] = relationship("Chart", back_populates="sources")