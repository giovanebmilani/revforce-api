from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.config.database import Base

class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(primary_key=True)
    remote_id: Mapped[str]
    integration_id: Mapped[str] = mapped_column(ForeignKey("account_configs.id"))
    name: Mapped[str]
    start_date: Mapped[datetime | None] = mapped_column(nullable=True)
    end_date: Mapped[datetime | None] = mapped_column(nullable=True)
    daily_budget: Mapped[float | None] = mapped_column(nullable=True)
    monthly_budget: Mapped[float | None] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now)

    def __init__(self, remote_id: str, integration_id: str, name: str, start_date: str | datetime, end_date: str | datetime, daily_budget: str | None, monthly_budget: str | None):
        self.remote_id = remote_id
        self.integration_id = integration_id
        self.name = name
        
        if daily_budget is not None:
            self.daily_budget = float(daily_budget)
        
        if monthly_budget is not None:
            self.monthly_budget = float(monthly_budget)
        
        if isinstance(start_date, str) and start_date is not None:
            self.start_date = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)

        if isinstance(end_date, str) and end_date is not None:
            self.end_date = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
