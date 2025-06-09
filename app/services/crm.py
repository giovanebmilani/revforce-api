from fastapi import Depends, HTTPException
from starlette import status
import uuid

from app.services.activecampaign_service import get_deals
from app.models.deal import Deal
from app.repositories.account_config import AccountConfigRepository
from app.repositories.deal import DealRepository
from app.repositories.contact import ContactRepository
from app.repositories.message import MessageRepository


class CrmService:
    def __init__(
        self,
        account_config_repository: AccountConfigRepository,
        deal_repository: DealRepository,
        contact_repository: ContactRepository,
        message_repository: MessageRepository,
    ):
        self.__account_config_repository = account_config_repository
        self.__deal_repository = deal_repository
        self.__contact_repository = contact_repository
        self.__message_repository = message_repository


    async def fetch_new_data(self, config_id: str):
        config = await self.__account_config_repository.get(config_id)

        if config is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account Config not found."
            )

        # TODO: use the config.api_secret
        deals = await get_deals()

        for deal in deals:
            # TODO: test this beacause I don't have the integration configured
            await self.__deal_repository.create(Deal(
                integration_id=config_id,
                remote_id=deal.get("id", str(uuid.uuid4())),
                contact_id=deal.get("contact_id"),
                title=deal.get("title", ""),
                status=deal.get("status", ""),
                value=deal.get("value", 0.0),
                currency=deal.get("currency", "USD"),
                created_at=deal.get("created_at"),
                closed_at=deal.get("closed_at", None),
            ))

        pass


    @classmethod
    async def get_service(
        cls,
        account_config_repository: AccountConfigRepository = Depends(AccountConfigRepository.get_repository),
        deal_repository: DealRepository = Depends(DealRepository.get_repository),
        contact_repository: ContactRepository = Depends(ContactRepository.get_repository),
        message_repository: MessageRepository = Depends(MessageRepository.get_repository),
    ):
        return cls(account_config_repository, deal_repository, contact_repository, message_repository)