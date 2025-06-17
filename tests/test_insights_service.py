import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import httpx 
from httpx import Response 
from fastapi import HTTPException, Depends 
from starlette import status

# Add the parent directory to the Python path to allow importing from 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.insights import InsightsService
from app.config.application import settings, get_http_client 

# --- Fixtures ---

@pytest_asyncio.fixture
def mock_http_client():
    """Mocks the httpx.AsyncClient dependency."""
    return AsyncMock(spec=httpx.AsyncClient)

@pytest_asyncio.fixture
def insights_service(mock_http_client):
    """Provides an instance of InsightsService with mocked dependencies."""
    return InsightsService(http_client=mock_http_client)

@pytest_asyncio.fixture(autouse=True)
def mock_settings_for_insights_service():
    """
    **FIX:** Patches the 'settings' object directly within the 'app.services.insights' module's namespace.
    This ensures that when `InsightsService` accesses `settings.API_KEY`, it refers to our mock.
    We explicitly add the `API_KEY` attribute to the mocked settings object.
    """
    with patch('app.services.insights.settings') as mock_settings_in_insights:
        mock_settings_in_insights.API_KEY = "test_api_key_mocked_for_service"
        yield mock_settings_in_insights

# --- Test Cases for get_insights ---

@pytest.mark.asyncio
async def test_get_insights_success(insights_service, mock_http_client, mock_settings_for_insights_service):
    """
    Testa a recuperação bem-sucedida de insights da API da OpenAI.
    """
    prompt = "Qual a tendência de mercado para 2024?"
    openai_response_content = "A principal tendência para 2024 é a IA generativa."

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [
            {"message": {"content": openai_response_content}}
        ]
    }
    mock_response.raise_for_status.return_value = None 
    mock_http_client.post.return_value = mock_response

    expected_url = "https://api.openai.com/v1/chat/completions"
    expected_headers = {
        "Authorization": f"Bearer {mock_settings_for_insights_service.API_KEY}",
        "Content-Type": "application/json"
    }
    expected_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150
    }

    result = await insights_service.get_insights(prompt)

    mock_http_client.post.assert_awaited_once_with(
        expected_url,
        json=expected_data,
        headers=expected_headers
    )
    mock_response.raise_for_status.assert_called_once()
    assert result == {"response": openai_response_content}

@pytest.mark.asyncio
async def test_get_insights_http_status_error(insights_service, mock_http_client, mock_settings_for_insights_service):
    """
    Testa o cenário onde a API da OpenAI retorna um erro HTTP (e.g., 401, 404, 500).
    Espera que uma HTTPException seja levantada com o status e detalhe corretos.
    """
    prompt = "Erro na API."
    error_status_code = 401
    error_detail_text = "Invalid API key."

    mock_response = MagicMock(spec=Response)
    mock_response.status_code = error_status_code
    mock_response.text = error_detail_text
    
    http_status_error = httpx.HTTPStatusError(
        f"Server error {error_status_code} for URL: {mock_http_client.post.call_args[0][0] if mock_http_client.post.call_args else 'N/A'}",
        request=MagicMock(spec=httpx.Request),
        response=mock_response
    )
    mock_http_client.post.side_effect = http_status_error

    with pytest.raises(HTTPException) as exc_info:
        await insights_service.get_insights(prompt)
    
    assert exc_info.value.status_code == error_status_code
    assert exc_info.value.detail == error_detail_text
    mock_http_client.post.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_insights_generic_exception(insights_service, mock_http_client, mock_settings_for_insights_service):
    """
    Testa o cenário onde ocorre uma exceção genérica durante a comunicação com a API da OpenAI
    (e.g., erro de rede, problema de JSON).
    Espera que uma HTTPException 500_INTERNAL_SERVER_ERROR seja levantada.
    """
    prompt = "Erro inesperado."
    generic_error_message = "Network connection failed."

    mock_http_client.post.side_effect = Exception(generic_error_message)

    with pytest.raises(HTTPException) as exc_info:
        await insights_service.get_insights(prompt)
    
    assert exc_info.value.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exc_info.value.detail == generic_error_message
    mock_http_client.post.assert_awaited_once()


# --- Test Cases for get_service ---

@pytest.mark.asyncio
async def test_get_service(mock_http_client):
    """
    Testa o método de classe get_service para injeção de dependência.
    """
    service_instance = await InsightsService.get_service(http_client=mock_http_client)
    assert isinstance(service_instance, InsightsService)
    assert service_instance.http_client == mock_http_client