from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey
from app.config.database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id: Mapped[str] = mapped_column(primary_key=True)
    remote_id: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]
    created_at: Mapped[datetime]
    source: Mapped[str]
