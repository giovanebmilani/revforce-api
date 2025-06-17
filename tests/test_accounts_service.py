import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from starlette import status
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.services.accounts import AccountService
from app.models.account import Account
from app.schemas.accounts import AccountRequest

@pytest_asyncio.fixture
def mock_repository():
    repo = AsyncMock()
    return repo

@pytest_asyncio.fixture
def service(mock_repository):
    return AccountService(mock_repository)

@pytest.mark.asyncio
async def test_get_account_found(service, mock_repository):
    mock_account = Account(id="123", name="Test Account")
    mock_repository.get.return_value = mock_account

    result = await service.get_account("123")

    assert result == mock_account
    mock_repository.get.assert_awaited_once_with("123")

@pytest.mark.asyncio
async def test_get_account_not_found(service, mock_repository):
    mock_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_account("not_exists")

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert "Account not found" in exc_info.value.detail

@pytest.mark.asyncio
async def test_create_account_success(service, mock_repository):
    account_request = AccountRequest(name="New Account")

    mock_repository.get_by_name.return_value = None
    mock_repository.create.return_value = Account(id="abc123", name="New Account")

    result = await service.create_account(account_request)

    assert result.id == "abc123"
    assert result.name == "New Account"
    mock_repository.get_by_name.assert_awaited_once_with("New Account")
    mock_repository.create.assert_awaited_once_with("New Account")

@pytest.mark.asyncio
async def test_create_account_conflict(service, mock_repository):
    account_request = AccountRequest(name="Conflict Account")
    mock_repository.get_by_name.return_value = Account(id="existing", name="Conflict Account")

    with pytest.raises(HTTPException) as exc_info:
        await service.create_account(account_request)

    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert "already exists" in exc_info.value.detail

@pytest.mark.asyncio
async def test_update_account_success(service, mock_repository):
    account_id = "123"
    account_request = AccountRequest(name="Updated Name")

    mock_repository.get.return_value = Account(id=account_id, name="Old Name")
    mock_repository.update.return_value = Account(id=account_id, name="Updated Name")

    result = await service.update_account(account_id, account_request)

    assert result.name == "Updated Name"
    mock_repository.get.assert_awaited_once_with(account_id)
    mock_repository.update.assert_awaited_once()

@pytest.mark.asyncio
async def test_update_account_not_found(service, mock_repository):
    mock_repository.get.return_value = None
    account_request = AccountRequest(name="Updated Name")

    with pytest.raises(HTTPException) as exc_info:
        await service.update_account("not_found", account_request)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_account(service, mock_repository):
    account_id = "123"
    await service.delete_account(account_id)

    mock_repository.delete.assert_awaited_once_with(account_id)