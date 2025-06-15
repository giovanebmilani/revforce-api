import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock, call
import sys
import os
import uuid
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException 
from starlette import status

# Add the parent directory to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.refresh import RefreshService
from app.repositories.account_config import AccountConfigRepository 
from app.models.account_config import AccountType 
from app.models.account_config import AccountConfig 
from app.schemas.refresh import RefreshRequest, RefreshResponse

# --- Fixtures ---

@pytest_asyncio.fixture
def mock_account_config_repository():
    """Mocks the AccountConfigRepository dependency."""
    return AsyncMock(spec=AccountConfigRepository) 

@pytest_asyncio.fixture
def refresh_service(mock_account_config_repository):
    """Provides an instance of RefreshService with mocked dependencies."""
    return RefreshService(account_config_repository=mock_account_config_repository)


# --- Test Cases for get_refresh_time ---

@pytest.mark.asyncio
async def test_get_refresh_time_success_multiple_configs(refresh_service, mock_account_config_repository):
    """
    Testa a recuperação do tempo de refresh quando há múltiplas configurações de conta,
    encontrando a mais antiga.
    """
    account_id = str(uuid.uuid4())
    now = datetime(2025, 1, 1, 10, 0, 0)

    config_latest = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.google_ads, last_refresh=now)
    config_middle = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.facebook_ads, last_refresh=now - timedelta(minutes=30))
    config_oldest = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.crm, last_refresh=now - timedelta(hours=1))

    mock_account_config_repository.get_by_account_id.return_value = [
        config_latest, config_oldest, config_middle
    ]

    expected_refresh_time_str = config_oldest.last_refresh.strftime("%Y-%m-%d %H:%M:%S")

    response = await refresh_service.get_refresh_time(account_id)

    mock_account_config_repository.get_by_account_id.assert_awaited_once_with(account_id)
    assert isinstance(response, RefreshResponse)
    assert response.next_refresh_time == expected_refresh_time_str

@pytest.mark.asyncio
async def test_get_refresh_time_success_single_config(refresh_service, mock_account_config_repository):
    """
    Testa a recuperação do tempo de refresh quando há apenas uma configuração de conta.
    """
    account_id = str(uuid.uuid4())
    now = datetime(2025, 1, 1, 10, 0, 0)
    single_config = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.google_ads, last_refresh=now)

    mock_account_config_repository.get_by_account_id.return_value = [single_config]
    expected_refresh_time_str = single_config.last_refresh.strftime("%Y-%m-%d %H:%M:%S")

    response = await refresh_service.get_refresh_time(account_id)

    mock_account_config_repository.get_by_account_id.assert_awaited_once_with(account_id)
    assert isinstance(response, RefreshResponse)
    assert response.next_refresh_time == expected_refresh_time_str

@pytest.mark.asyncio
async def test_get_refresh_time_account_configs_not_found(refresh_service, mock_account_config_repository):
    """
    Testa a recuperação do tempo de refresh quando não há configurações de conta,
    esperando um HTTPException 404.
    """
    account_id = str(uuid.uuid4())
    mock_account_config_repository.get_by_account_id.return_value = [] 

    with pytest.raises(HTTPException) as exc_info:
        await refresh_service.get_refresh_time(account_id)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Account Configs not found."
    mock_account_config_repository.get_by_account_id.assert_awaited_once_with(account_id)

@pytest.mark.asyncio
async def test_get_refresh_time_with_none_last_refresh(refresh_service, mock_account_config_repository):
    """
    Testa o cenário onde algumas configurações têm last_refresh como None.
    A lógica deve ignorar None e encontrar a data mais antiga entre as não-None.
    """
    account_id = str(uuid.uuid4())
    now = datetime(2025, 1, 1, 10, 0, 0)

    config_none_refresh = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.google_ads, last_refresh=None)
    config_oldest = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.facebook_ads, last_refresh=now - timedelta(hours=2))
    config_latest = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.crm, last_refresh=now - timedelta(hours=1))

    mock_account_config_repository.get_by_account_id.return_value = [
        config_latest, config_oldest, config_none_refresh 
    ]

    expected_refresh_time_str = config_oldest.last_refresh.strftime("%Y-%m-%d %H:%M:%S")

    response = await refresh_service.get_refresh_time(account_id)
    mock_account_config_repository.get_by_account_id.assert_awaited_once_with(account_id)
    assert isinstance(response, RefreshResponse)
    assert response.next_refresh_time == expected_refresh_time_str


# --- Test Cases for refresh ---

@pytest.mark.asyncio
async def test_refresh_all_configs_updated(refresh_service, mock_account_config_repository):
    """
    Testa o refresh de todas as configurações quando seus tempos de refresh são antigos.
    Verifica se a integração correta é chamada e last_refresh é atualizado.
    """
    account_id = str(uuid.uuid4())
    mock_current_time = datetime(2025, 1, 1, 10, 0, 0)

    config_google = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.google_ads, last_refresh=mock_current_time - timedelta(hours=4))
    config_facebook = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.facebook_ads, last_refresh=mock_current_time - timedelta(hours=5))
    config_crm = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.crm, last_refresh=mock_current_time - timedelta(days=1))

    mock_account_config_repository.get_by_account_id.return_value = [
        config_google, config_facebook, config_crm
    ]
    mock_account_config_repository.update.return_value = MagicMock() 

    refresh_request = RefreshRequest(account_id=account_id)

    with patch('app.services.refresh.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_current_time
        with patch('builtins.print') as mock_print:

            await refresh_service.refresh(refresh_request)

            mock_account_config_repository.get_by_account_id.assert_awaited_once_with(account_id)
            assert mock_account_config_repository.update.call_count == 3

            assert config_google.last_refresh == mock_current_time
            assert config_facebook.last_refresh == mock_current_time
            assert config_crm.last_refresh == mock_current_time

            mock_account_config_repository.update.assert_any_call(config_google.id, config_google)
            mock_account_config_repository.update.assert_any_call(config_facebook.id, config_facebook)
            mock_account_config_repository.update.assert_any_call(config_crm.id, config_crm)

            mock_print.assert_any_call("integração com google ads chamada")
            mock_print.assert_any_call("integração com facebook ads chamada")
            mock_print.assert_any_call("integração com crm chamada")


@pytest.mark.asyncio
async def test_refresh_some_configs_skipped(refresh_service, mock_account_config_repository):
    """
    Testa o refresh onde algumas configurações são atualizadas e outras são puladas
    porque seus tempos de refresh são recentes.
    """

    account_id = str(uuid.uuid4())
    mock_current_time = datetime(2025, 1, 1, 10, 0, 0)

    config_old = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.google_ads, last_refresh=mock_current_time - timedelta(hours=4))
    config_recent = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.facebook_ads, last_refresh=mock_current_time - timedelta(hours=1))
    config_no_refresh = AccountConfig(id=str(uuid.uuid4()), account_id=account_id, type=AccountType.crm, last_refresh=None)

    mock_account_config_repository.get_by_account_id.return_value = [
        config_old, config_recent, config_no_refresh
    ]
    mock_account_config_repository.update.return_value = MagicMock()

    refresh_request = RefreshRequest(account_id=account_id)

    with patch('app.services.refresh.datetime') as mock_datetime:
        mock_datetime.now.return_value = mock_current_time
        with patch('builtins.print') as mock_print:
            await refresh_service.refresh(refresh_request)
            mock_account_config_repository.get_by_account_id.assert_awaited_once_with(account_id)
            assert mock_account_config_repository.update.call_count == 2
            assert config_old.last_refresh == mock_current_time
            assert config_recent.last_refresh == mock_current_time - timedelta(hours=1)
            assert config_no_refresh.last_refresh == mock_current_time
            mock_account_config_repository.update.assert_any_call(config_old.id, config_old)
            mock_account_config_repository.update.assert_any_call(config_no_refresh.id, config_no_refresh)
            mock_print.assert_any_call("integração com google ads chamada")
            mock_print.assert_any_call("integração com crm chamada")
            assert call("integração com facebook ads chamada") not in mock_print.call_args_list


@pytest.mark.asyncio
async def test_refresh_account_configs_not_found(refresh_service, mock_account_config_repository):
    """
    Testa o refresh quando não há configurações de conta,
    esperando um HTTPException 404.
    """
    account_id = str(uuid.uuid4())
    mock_account_config_repository.get_by_account_id.return_value = [] 

    refresh_request = RefreshRequest(account_id=account_id)

    with pytest.raises(HTTPException) as exc_info:
        await refresh_service.refresh(refresh_request)

    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Account Configs not found."
    mock_account_config_repository.get_by_account_id.assert_awaited_once_with(account_id)
    mock_account_config_repository.update.assert_not_awaited() 

@pytest.mark.asyncio
async def test_get_service(mock_account_config_repository):
    """Testa o método de classe get_service."""
    service_instance = await RefreshService.get_service(account_config_repository=mock_account_config_repository)
    assert isinstance(service_instance, RefreshService)
    assert service_instance._RefreshService__repository == mock_account_config_repository