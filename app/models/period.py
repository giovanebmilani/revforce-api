import enum
from sqlalchemy import Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class PeriodType(str, enum.Enum):
    month = "month"
    week = "week"
    day = "day"
    hour = "hour"

class Period(Base):
    __tablename__ = "periods"

    id: Mapped[str] = mapped_column(primary_key=True)
    type: Mapped[PeriodType] = mapped_column(Enum(PeriodType))
    amount: Mapped[int]