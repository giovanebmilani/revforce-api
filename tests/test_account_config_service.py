import pytest
import pytest_asyncio
from unittest.mock import AsyncMock
from fastapi import HTTPException
from starlette import status
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.account_config import AccountConfigService
from app.schemas.account_config import AccountConfigRequest
from app.models.account_config import AccountConfig, AccountType
from app.models.account import Account


@pytest_asyncio.fixture
def mock_repository():
    return AsyncMock()


@pytest_asyncio.fixture
def mock_account_service():
    return AsyncMock()


@pytest_asyncio.fixture
def service(mock_repository, mock_account_service):
    return AccountConfigService(mock_repository, mock_account_service)


@pytest.mark.asyncio
async def test_get_config_found(service, mock_repository):
    mock_config = AccountConfig(account_id="acc-1", type=AccountType.google_ads, api_secret="secret")
    mock_repository.get.return_value = mock_config

    result = await service.get_config("cfg-1")

    assert result == mock_config
    mock_repository.get.assert_awaited_once_with("cfg-1")


@pytest.mark.asyncio
async def test_get_config_not_found(service, mock_repository):
    mock_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.get_config("missing-id")

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_create_config_success(service, mock_repository, mock_account_service):
    account_id = "acc-1"
    account = Account(id=account_id, name="Test Account")
    config_request = AccountConfigRequest(account_id=account_id, type=AccountType.google_ads, api_secret="abc123")

    mock_account_service.get_account.return_value = account
    mock_repository.create.return_value = AccountConfig(account_id=account_id, type=AccountType.google_ads, api_secret="abc123")

    result = await service.create_config(config_request)

    assert result.account_id == account_id
    assert result.type == AccountType.google_ads
    assert result.api_secret == "abc123"
    mock_account_service.get_account.assert_awaited_once_with(account_id)
    mock_repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_config_success(service, mock_repository):
    config_id = "cfg-1"
    config_request = AccountConfigRequest(account_id="acc-1", type=AccountType.crm, api_secret="newsecret")

    mock_repository.get.return_value = AccountConfig(account_id="acc-1", type=AccountType.google_ads, api_secret="old")
    mock_repository.update.return_value = AccountConfig(account_id="acc-1", type=AccountType.crm, api_secret="newsecret")

    result = await service.update_config(config_id, config_request)

    assert result.type == AccountType.crm
    assert result.api_secret == "newsecret"
    mock_repository.get.assert_awaited_once_with(config_id)
    mock_repository.update.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_config_not_found(service, mock_repository):
    mock_repository.get.return_value = None
    config_request = AccountConfigRequest(account_id="acc-1", type=AccountType.crm, api_secret="abc")

    with pytest.raises(HTTPException) as exc:
        await service.update_config("nonexistent", config_request)

    assert exc.value.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
async def test_delete_config(service, mock_repository):
    await service.delete_config("cfg-1")
    mock_repository.delete.assert_awaited_once_with("cfg-1")

