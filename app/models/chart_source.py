from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum
import enum

from app.config.database import Base

class SourceTable(str, enum.Enum):
    campaign = 'campaign'
    ad = 'ad'

class ChartSource(Base):
    __tablename__ = "chart_sources"
    id: Mapped[str] = mapped_column(primary_key=True)
    chart_id: Mapped[str] = mapped_column(ForeignKey('charts.id'))
    source_id: Mapped[str]
    source_table: Mapped[SourceTable] = mapped_column(Enum(SourceTable))