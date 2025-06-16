from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, Enum
import enum

from app.config.database import Base
from . import Event

from .period import Period
from .chart_source import ChartSource

class ChartType(str, enum.Enum):
    pizza = 'pizza'
    line = 'line'
    bar = 'bar'
    horizontal_bar = 'horizontal_bar'
    grouped_bar = 'grouped_bar'

class ChartSegment(str, enum.Enum):
    device = 'device'
    date = 'date'

class Chart(Base):
    __tablename__ = "charts"

    id: Mapped[str] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    name: Mapped[str]
    type: Mapped[ChartType] = mapped_column(Enum(ChartType))
    period_id: Mapped[str] = mapped_column(ForeignKey("periods.id"))
    granularity_id: Mapped[str] = mapped_column(ForeignKey("periods.id"))
    segment: Mapped[ChartSegment | None] = mapped_column(Enum(ChartSegment))
    position: Mapped[int] = mapped_column() # sem constraint unique, isso é verificado no service

    period: Mapped["Period"] = relationship("Period", foreign_keys=[period_id], single_parent=True, cascade="all, delete-orphan")
    granularity: Mapped["Period"] = relationship("Period", foreign_keys=[granularity_id], single_parent=True, cascade="all, delete-orphan")
    # Relacionamento reverso
    sources: Mapped[list["ChartSource"]] = relationship("ChartSource", cascade="all, delete-orphan")
    events: Mapped[list["Event"]] = relationship("Event", backref="chart", cascade="all, delete-orphan")

