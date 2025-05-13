import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum

import app.models.ad

from app.config.database import Base

class DeviceType(str, enum.Enum):
    mobile = 'mobile'
    desktop = 'desktop'
    tablet = 'tablet'
    other = 'other'

class AdMetric(Base):
    __tablename__ = "ad_metrics"

    id: Mapped[str] = mapped_column(primary_key=True)
    ad_id: Mapped[str] = mapped_column(ForeignKey("ads.id"))
    ctr: Mapped[int]
    impressions: Mapped[int]
    views: Mapped[int]
    clicks: Mapped[int]
    device: Mapped[DeviceType] = mapped_column(Enum(DeviceType))
    date: Mapped[datetime]
    hour: Mapped[int]
    day: Mapped[int]
    month: Mapped[int]
    year: Mapped[int]
