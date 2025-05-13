from fastapi import Depends, HTTPException
from starlette import status

from app.services.accounts import AccountService

from app.repositories.account_config import AccountConfigRepository
from app.schemas.account_config import AccountConfigRequest
from app.models.account_config import AccountConfig

class AccountConfigService:
    def __init__(self, account_config_repository: AccountConfigRepository, account_service: AccountService):
        self.__repository = account_config_repository
        self.__account_service = account_service

    async def get_config(self, config_id: str):
        config = await self.__repository.get(config_id)

        if config is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AccountConfig not found.")
        
        return config

    async def create_config(self, config: AccountConfigRequest):
        # esse método levanta uma excessão se não encontrar a conta, então ela existe
        account = await self.__account_service.get_account(config.account_id)

        config = await self.__repository.create(AccountConfig(
            account_id=account.id,
            type=config.type,
            api_secret=config.api_secret
        ))

        return config

    async def update_config(self, config_id: str, config: AccountConfigRequest):
        db_config = await self.__repository.get(config_id)

        if db_config is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="AccountConfig not found.")

        updated_config = await self.__repository.update(config_id, AccountConfig(
            account_id=config.account_id,
            type=config.type,
            api_secret=config.api_secret
        ))

        return updated_config

    async def delete_config(self, config_id: str):
        await self.__repository.delete(config_id)

    @classmethod
    async def get_service(
        cls, 
        account_config_repository: AccountConfigRepository = Depends(AccountConfigRepository.get_service), 
        account_service: AccountService = Depends(AccountService.get_service)
    ):
        """ Dependency to inject the service into routes """
        return cls(account_config_repository, account_service)


