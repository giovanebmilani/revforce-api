from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.config.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(primary_key=True)
    remote_id: Mapped[str]
    integration_id: Mapped[str]
    name: Mapped[str]
    start_date: Mapped[datetime]
    end_date: Mapped[datetime]
    daily_budget: Mapped[float]
    monthly_budget: Mapped[float]
