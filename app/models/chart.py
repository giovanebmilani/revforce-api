from typing import List, TYPE_CHECKING
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum
import enum

from app.config.database import Base

if TYPE_CHECKING:
    from .period import Period
    from .chart_source import ChartSource

class ChartType(str, enum.Enum):
    pizza = 'pizza'
    line = 'line'
    bar = 'bar'
    horizontal_bar = 'horizontal_bar'
    grouped_bar = 'grouped_bar'

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
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    name: Mapped[str]
    type: Mapped[ChartType] = mapped_column(Enum(ChartType))
    metric: Mapped[ChartMetric] = mapped_column(Enum(ChartMetric))
    period_id: Mapped[str] = mapped_column(ForeignKey("periods.id"))
    granularity_id: Mapped[str] = mapped_column(ForeignKey("periods.id"))
    segment: Mapped[ChartSegment | None] = mapped_column(Enum(ChartSegment))
    position: Mapped[int] = mapped_column() # sem constraint unique, isso é verificado no service

    period: Mapped["Period"] = relationship("Period", foreign_keys=[period_id], single_parent=True, cascade="all, delete-orphan")
    granularity: Mapped["Period"] = relationship("Period", foreign_keys=[granularity_id], single_parent=True, cascade="all, delete-orphan")
    # Relacionamento reverso
    sources: Mapped[List["ChartSource"]] = relationship("ChartSource", cascade="all, delete-orphan")
