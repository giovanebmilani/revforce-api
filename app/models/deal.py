from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey

from app.config.database import Base

class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[str] = mapped_column(primary_key=True)
    remote_id: Mapped[str] = mapped_column(unique=True)
    contact_id: Mapped[str]
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    title: Mapped[str]
    status: Mapped[str]
    value: Mapped[float]
    currency: Mapped[str]
    created_at: Mapped[datetime]
    closed_at: Mapped[datetime]
