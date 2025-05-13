from sqlalchemy.orm import Mapped, mapped_column

from app.config.database import Base


class Account(Base): 
    __tablename__ = "accounts"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] 

