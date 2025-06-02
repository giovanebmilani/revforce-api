from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.config.database import Base

class Event(Base):
    __tablename__ = "events"
    id: Mapped[str] = mapped_column(primary_key=True)
    chart_id: Mapped[str] = mapped_column(ForeignKey('charts.id', ondelete="CASCADE"))
    name: Mapped[str]
    description: Mapped[str]
    date: Mapped[datetime]
    color: Mapped[str]