import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.openai import OpenAIService
from app.config.application import settings 
from app.schemas.chat import AssistantIntegration, History, Role 

# --- Fixtures ---

@pytest_asyncio.fixture
def mock_openai_client():
    """
    Mocks the `openai.OpenAI` client and its methods.
    **FIX:** We mock `client.responses.create` as a regular MagicMock (synchronous).
    """
    mock_client = MagicMock()
    mock_client.responses = MagicMock() 
    mock_client.responses.create = MagicMock() 
    return mock_client

@pytest_asyncio.fixture
def openai_service(mock_openai_client):
    """
    Provides an instance of OpenAIService with a mocked OpenAI client.
    We'll patch the global 'client' object in the OpenAIService module.
    """
    with patch('app.services.openai.client', new=mock_openai_client):
        yield OpenAIService()

@pytest_asyncio.fixture(autouse=True)
def mock_settings_openai_key():
    """
    Patches settings.OPENAI_KEY for testing purposes.
    This ensures that the global client initialization (if it happens) or any direct
    access to settings.OPENAI_KEY uses a test key.
    """
    with patch('app.config.application.settings.OPENAI_KEY', "test_openai_api_key"):
        yield

# --- Test Cases ---

@pytest.mark.asyncio
async def test_chat_gpt_success(openai_service, mock_openai_client):
    """
    Testa a comunicação bem-sucedida com a API do OpenAI via chat_gpt.
    """
    assist_integration_data = AssistantIntegration(
        model="gpt-3.5-turbo",
        messages=[
            History(role=Role.user, content="Olá, como você está?"),
            History(role=Role.assistant, content="Estou bem, obrigado! Como posso ajudar?")
        ]
    )
    
    mock_response_object = MagicMock()
    mock_response_object.output_text = "Estou pronto para ajudar!"
    mock_openai_client.responses.create.return_value = mock_response_object

    result = await openai_service.chat_gpt(assist_integration_data)

    mock_openai_client.responses.create.assert_called_once_with(
        model=assist_integration_data.model,
        input=assist_integration_data.messages
    )
    assert result == "Estou pronto para ajudar!"

@pytest.mark.asyncio
async def test_chat_gpt_api_error(openai_service, mock_openai_client):
    """
    Testa o tratamento de erros da API do OpenAI (e.g., falha de conexão, erro do servidor).
    """
    assist_integration_data = AssistantIntegration(
        model="gpt-3.5-turbo",
        messages=[History(role=Role.user, content="Gere um erro.")]
    )
    
    mock_openai_client.responses.create.side_effect = Exception("Erro interno da API do OpenAI.")

    with pytest.raises(Exception) as exc_info: 
        await openai_service.chat_gpt(assist_integration_data)
    
    mock_openai_client.responses.create.assert_called_once_with(
        model=assist_integration_data.model,
        input=assist_integration_data.messages
    )
    assert "Erro interno da API do OpenAI." in str(exc_info.value)


@pytest.mark.asyncio
async def test_get_service(openai_service):
    """
    Testa o método de classe get_service.
    """
    service_instance = await OpenAIService.get_service()
    assert isinstance(service_instance, OpenAIService)