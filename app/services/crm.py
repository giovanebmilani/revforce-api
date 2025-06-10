from fastapi import Depends, HTTPException
from starlette import status
import uuid

from app.services.activecampaign_service import get_deals, get_contacts, get_messages
from app.models.deal import Deal
from app.models.message import Message
from app.models.contact import Contact
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

            # TODO: test this beacause I don't have the integration configured
        await self.__deal_repository.create_many([
            Deal(
                integration_id=config_id,
                remote_id=deal.get("id", str(uuid.uuid4())),
                contact_id=deal.get("contact_id"),
                title=deal.get("title", ""),
                status=deal.get("status", ""),
                value=deal.get("value", 0.0),
                currency=deal.get("currency", "USD"),
                created_at=deal.get("created_at"),
                closed_at=deal.get("closed_at", None),
            ) for deal in deals])

        messages = await get_messages()

        await self.__message_repository.create_many([
            Message(
                integration_id=config_id,
                remote_id=message.get("id", str(uuid.uuid4())),
                contact_id=message.get("contact_id"),
                content=message.get("content", ""),
                created_at=message.get("created_at"),
            ) for message in messages])
        
        contacts = await get_contacts()

        await self.__contact_repository.create_many([
            Contact(
                remote_id=contact.get("id", str(uuid.uuid4())),
                email=contact.get("email", ""),
                first_name=contact.get("first_name", ""),
                created_at=contact.get("created_at"),
                source=config.integration_type
            ) for contact in contacts])

        pass


    @classmethod
    async def get_service(
        cls,
        account_config_repository: AccountConfigRepository = Depends(AccountConfigRepository.get_service),
        deal_repository: DealRepository = Depends(DealRepository.get_service),
        contact_repository: ContactRepository = Depends(ContactRepository.get_service),
        message_repository: MessageRepository = Depends(MessageRepository.get_service),
    ):
        return cls(account_config_repository, deal_repository, contact_repository, message_repository)