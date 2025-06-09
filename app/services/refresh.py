from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from starlette import status

from app.models.account_config import AccountType
from app.repositories.account_config import AccountConfigRepository
from app.schemas.refresh import RefreshRequest, RefreshResponse

from app.services.crm import CrmService


class RefreshService:
    def __init__(self, account_config_repository: AccountConfigRepository, crm_service: CrmService):
        self.__repository = account_config_repository
        self.__crm_service = crm_service

    async def get_refresh_time(self, account_id: str):
        account_configs = await self.__repository.get_by_account_id(account_id)

        if account_configs is None or len(account_configs) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account Configs not found.")

        oldest_refresh_time = account_configs[0].last_refresh

        for accountConfig in account_configs:
            if accountConfig.last_refresh is not None and accountConfig.last_refresh < oldest_refresh_time:
                oldest_refresh_time = accountConfig.last_refresh

        return RefreshResponse(next_refresh_time=oldest_refresh_time.strftime("%Y-%m-%d %H:%M:%S"))

    async def refresh(self, refresh_data: RefreshRequest):
        account_configs = await self.__repository.get_by_account_id(refresh_data.account_id)

        if account_configs is None or len(account_configs) == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account Configs not found.")

        for accountConfig in account_configs:
            if accountConfig.last_refresh is not None and accountConfig.last_refresh + timedelta(
                    hours=3) > datetime.now():
                continue

            if accountConfig.type == AccountType.google_ads:
                # chamar integracao com google ads
                print("integração com google ads chamada")

            if accountConfig.type == AccountType.facebook_ads:
                # chamar integracao com facebook
                print("integração com facebook ads chamada")

            if accountConfig.type == AccountType.crm:
                # chamar integracao com crm
                self.__crm_service.fetch_new_data(accountConfig.id)
                print("integração com crm chamada")

            accountConfig.last_refresh = datetime.now()
            await self.__repository.update(accountConfig.id, accountConfig)

        return

    @classmethod
    async def get_service(
        cls, 
        account_config_repository: AccountConfigRepository = Depends(AccountConfigRepository.get_service),
        crm_service: CrmService = Depends(CrmService.get_service)
    ):
        return cls(account_config_repository, crm_service)
