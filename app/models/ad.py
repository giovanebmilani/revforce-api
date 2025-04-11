from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.config.database import Base

class Ad(Base):
    __tablename__ = "ads"

    id: Mapped[str] = mapped_column(primary_key=True)
    remote_id: Mapped[str]
    integration_id: Mapped[str] = mapped_column(ForeignKey("account_configs.id"))
    campaign_id: Mapped[str] = mapped_column(ForeignKey("campaigns.id"))
    name: Mapped[str]
    created_at: Mapped[datetime]