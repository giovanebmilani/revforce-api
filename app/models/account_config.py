import enum
from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Enum, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class AccountType(str, enum.Enum):
    facebook_ads = 'facebook_ads'
    google_ads = 'google_ads'
    crm = 'crm'


class AccountConfig(Base):
    __tablename__ = "account_configs"

    id: Mapped[str] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey("accounts.id"))
    type: Mapped[AccountType] = mapped_column(Enum(AccountType))
    api_id: Mapped[str] = mapped_column(nullable=True)
    api_secret: Mapped[str] = mapped_column(nullable=True)
    access_token: Mapped[str]  = mapped_column(nullable=True)
    last_refresh: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
