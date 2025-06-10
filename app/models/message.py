from datetime import datetime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base

class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(primary_key=True)
    integration_id: Mapped[str] = mapped_column(ForeignKey("account_configs.id"))
    remote_id: Mapped[str] = mapped_column(unique=True)
    subject: Mapped[str]
    priority: Mapped[int]
    create_date: Mapped[datetime]
