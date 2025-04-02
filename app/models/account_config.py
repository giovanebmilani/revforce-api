import enum
from sqlalchemy import ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class AccountType(str, enum.Enum):
    google_ads = 'google_ads'
    facebook_ads = 'facebook_ads'
    crm = 'crm'

class AccountConfig(Base):
    __tablename__ = "account_config"
    
    id: Mapped[str] = mapped_column(primary_key=True)
    id_user: Mapped[str] = mapped_column(ForeignKey("account.id"))
    tipo: Mapped[AccountType] = mapped_column(Enum(AccountType))
    chave_api: Mapped[str]

