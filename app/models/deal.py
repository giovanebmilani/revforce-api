from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.config.database import Base

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(primary_key=True)
    integration_id: Mapped[str] = mapped_column(ForeignKey("account_configs.id"))
    remote_id: Mapped[str] = mapped_column(unique=True)
    contact_id: Mapped[str]
    title: Mapped[str]
    status: Mapped[str]
    value: Mapped[float]
    currency: Mapped[str]
    created_at: Mapped[datetime]
    closed_at: Mapped[datetime | None]
