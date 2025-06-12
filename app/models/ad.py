from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from app.config.database import Base
from app.models.campaign import Campaign

class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[str] = mapped_column(primary_key=True)
    remote_id: Mapped[str]
    integration_id: Mapped[str] = mapped_column(ForeignKey("account_configs.id"))
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"))
    name: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(nullable=True)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now())

    campaign: Mapped['Campaign'] = relationship()

    def __init__(self, remote_id: str, integration_id: str, campaign_id: str, name: str, created_at: str | datetime, campaign: Campaign):
        self.remote_id = remote_id
        self.integration_id = integration_id
        self.campaign_id = campaign_id
        self.name = name
        self.campaign = campaign
        if isinstance(created_at, str) and created_at is not None:
            self.created_at = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=None)
