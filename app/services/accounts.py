from fastapi import Depends, HTTPException
from starlette import status

from app.repositories.account import AccountRepository
from app.schemas.accounts import AccountRequest
from app.models.account import Account

class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self.__repository = account_repository

    async def get_account(self, account_id: str):
        account = await self.__repository.get(account_id)

        if account is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")
        
        return account

    async def create_account(self, account: AccountRequest):
        account_same_name = await self.__repository.get_by_name(account.name)

        if account_same_name is not None:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account with name already exists")

        account = await self.__repository.create(account.name)

        return account

    async def update_account(self, account_id: str, account: AccountRequest):
        account_exists = await self.__repository.get(account_id)

        if account_exists is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found.")

        account = await self.__repository.update(account_id, Account(id=account_id, name=account.name))

        return account

    async def delete_account(self, account_id: str):
        await self.__repository.delete(account_id)

    @classmethod
    async def get_service(cls, account_repository: AccountRepository = Depends(AccountRepository.get_service)):
        return cls(account_repository)