from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.config.database import get_db
from sqlalchemy import select
from starlette import status
from sqlalchemy import update
from sqlalchemy import delete
from uuid import uuid4

from app.schemas.accounts import AccountRequest
from app.models.account import Account

class AccountsService:
    def __init__(self, session: AsyncSession):
        self.__session = session

    async def get_account(self, account_id: str):
        result = await self.__session.execute(
            select(Account).where(Account.id == account_id)
        )

        account = result.scalar_one_or_none()

        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
        
        return account

    async def create_account(self, account: AccountRequest):
        result = await self.__session.execute(
            insert(Account)
                .values(name=account.name,id=str(uuid4()))
                .returning(Account.id)
        )

        await self.__session.commit()

        return result.scalar_one()

    async def update_account(self, account_id: str, account: AccountRequest):
        result = await self.__session.execute(
            update(Account).where(Account.id == account_id)
                .values(name=account.name)
                .returning(Account)
        )

        await self.__session.commit()

        return result.scalar_one() 

    async def delete_account(self, account_id: str):
        result = await self.__session.execute(
            delete(Account).where(Account.id == account_id)
        )

        await self.__session.commit()

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db)):
        """ Dependency to inject the service into routes """
        return cls(db)

