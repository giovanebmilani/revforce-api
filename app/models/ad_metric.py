import enum
from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey, Enum

from app.config.database import Base

class DeviceType(str, enum.Enum):
    mobile = 'mobile'
    desktop = 'desktop'
    tablet = 'tablet'
    other = 'other'

class AdMetric(Base):
    __tablename__ = "ads"

    id: Mapped[str] = mapped_column(primary_key=True)
    ad_id: Mapped[str] = mapped_column(ForeignKey("ads.id"))
    ctr: Mapped[int]
    impressions: Mapped[int]
    views: Mapped[int]
    clicks: Mapped[int]
    device: Mapped[DeviceType] = mapped_column(Enum(DeviceType))
    date: Mapped[datetime]
    hour: Mapped[int] = mapped_column(min=0, max=23)
    day: Mapped[int] = mapped_column(min=1, max=31)
    month: Mapped[int] = mapped_column(min=1, max=12)
    year: Mapped[int]
