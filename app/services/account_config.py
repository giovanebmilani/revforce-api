from fastapi import Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert
from app.config.database import get_db
from sqlalchemy import select
from starlette import status
from sqlalchemy import update
from sqlalchemy import delete
from uuid import uuid4

from app.services.accounts import AccountsService

from app.schemas.account_config import AccountConfigRequest
from app.models.account_config import AccountConfig

class AccountConfigService:
    def __init__(self, session: AsyncSession, account_service: AccountsService):
        self.__session = session
        self.__account_service = account_service

    async def get_config(self, config_id: str):
        result = await self.__session.execute(
            select(AccountConfig).where(AccountConfig.id == config_id)
        )

        config = result.scalar_one_or_none()

        if config is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account_config not found.")
        
        return config

    async def create_config(self, config: AccountConfigRequest):
        # esse método levanta uma excessão se não encontrar a conta, então ela existe
        account = await self.__account_service.get_account(config.id_user)

        result = await self.__session.execute(
            insert(AccountConfig)
                .values(
                    id=str(uuid4()),
                    id_user=account.id,
                    tipo=config.tipo,
                    chave_api=config.chave_api
                ).returning(AccountConfig)
        )

        await self.__session.commit()

        config = result.scalar_one()

        return config

    async def update_config(self, config_id: str, config: AccountConfigRequest):
        result = await self.__session.execute(
            update(AccountConfig).where(AccountConfig.id == config_id)
                .values(
                    tipo=config.tipo,
                    chave_api=config.chave_api
                )
                .returning(AccountConfig)
        )
        await self.__session.commit()

        return result.scalar_one() 

    async def delete_config(self, config_id: str):
        result = await self.__session.execute(
            delete(AccountConfig).where(AccountConfig.id == config_id)
        )

        await self.__session.commit()

    @classmethod
    async def get_service(cls, db: AsyncSession = Depends(get_db), account_service: AccountsService = Depends(AccountsService.get_service)):
        """ Dependency to inject the service into routes """
        return cls(db, account_service)


