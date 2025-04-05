from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum
import enum

from app.config.database import Base

class ChartType(str, enum.Enum):
    pizza = 'pizza'
    line = 'line'
    bar = 'bar'
    horizontal_bar = 'horizontal_bar'
    grouped_bar = 'grouped-bar'

class ChartMetric(str, enum.Enum):
    ctr = 'ctr'
    click = 'click'
    impression = 'impression'
    spend = 'spend'

class ChartSegment(str, enum.Enum):
    device = 'device'
    date = 'date'

class Chart(Base):
    __tablename__ = "charts"
    id: Mapped[str] = mapped_column(primary_key=True)
    account_id: Mapped[str]
    name: Mapped[str]
    type: Mapped[ChartType] = mapped_column(Enum(ChartType))
    metric: Mapped[ChartMetric] = mapped_column(Enum(ChartMetric))
    period: Mapped[str] = mapped_column(ForeignKey('periods.id'))
    granularity: Mapped[str] = mapped_column(ForeignKey('periods.id'))
    source: Mapped[str] = mapped_column(ForeignKey('chart_sources.id'))
    segment: Mapped[ChartSegment] = mapped_column(Enum(ChartSegment))

