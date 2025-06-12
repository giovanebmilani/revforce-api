from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.config.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(primary_key=True)
    integration_id: Mapped[str] = mapped_column(ForeignKey("account_configs.id"))
    remote_id: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str | None]
    created_at: Mapped[datetime]
    source: Mapped[str]
