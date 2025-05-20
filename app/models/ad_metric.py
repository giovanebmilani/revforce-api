import enum
from datetime import datetime

from dateutil import parser
from sqlalchemy import ForeignKey, Enum, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base
from app.utils.extension import Extension


class DeviceType(str, enum.Enum):
    mobile = 'mobile'
    desktop = 'desktop'
    tablet = 'tablet'
    other = 'other'


class AdMetric(Base):
    __tablename__ = "ad_metrics"

    id: Mapped[str] = mapped_column(primary_key=True)
    ad_id: Mapped[str] = mapped_column(ForeignKey("ads.id"))
    ctr: Mapped[float] = mapped_column(Float, nullable=True)
    impressions: Mapped[int] = mapped_column(nullable=True)
    views: Mapped[int] = mapped_column(nullable=True)
    clicks: Mapped[int] = mapped_column(nullable=True)
    device: Mapped[DeviceType] = mapped_column(Enum(DeviceType))
    spend: Mapped[int] = mapped_column(nullable=True)
    date: Mapped[datetime] = mapped_column(nullable=True)
    hour: Mapped[int] = mapped_column(nullable=True)
    day: Mapped[int] = mapped_column(nullable=True)
    month: Mapped[int] = mapped_column(nullable=True)
    year: Mapped[int] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def __init__(self, ad_id: str, ctr: float | None, impressions: int | None,
                 views: int | None, clicks: int | None, device: DeviceType,
                 date: datetime | None = None):
        self.ad_id = ad_id
        self.ctr = ctr
        self.impressions = impressions
        self.views = views
        self.clicks = clicks
        self.device = device
        self.date = date
        self.updated_at = datetime.now()

        if date:
            self.day = date.day
            self.month = date.month
            self.year = date.year
            self.hour = date.hour if date.time() != datetime.min.time() else None

    @classmethod
    def from_raw(cls, ad_id: str, ctr, impressions, views, clicks, device: str, date_raw) -> "AdMetric":
        parsed_date = parser.parse(date_raw) if date_raw else None
        return cls(
            ad_id=ad_id,
            ctr=Extension.try_parse_to_float(ctr),
            impressions=Extension.try_parse_to_int(impressions),
            views=Extension.try_parse_to_int(views),
            clicks=Extension.try_parse_to_int(clicks),
            device=cls.parse_device(device),
            date=parsed_date
        )

    def __repr__(self):
        return (
            f"<AdMetric(id={self.id}, ad_id={self.ad_id}, ctr={self.ctr}, "
            f"impressions={self.impressions}, views={self.views}, "
            f"clicks={self.clicks}, device={self.device}, date={self.date}), "
            f"hour={self.hour}, day={self.day}, month={self.month}, year={self.year}>"
        )

    @staticmethod
    def parse_device(device_str: str) -> DeviceType:
        if 'mobile' in device_str:
            return DeviceType.mobile
        if 'desktop' in device_str:
            return DeviceType.desktop
        if 'tablet' in device_str:
            return DeviceType.tablet
        return DeviceType.other
