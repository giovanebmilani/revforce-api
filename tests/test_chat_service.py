import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os
import uuid
from datetime import datetime, timedelta
import logging

from fastapi import HTTPException, Depends
from starlette import status

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.chat import ChatService
from app.services.charts import ChartService as ChartsService
from app.services.openai import OpenAIService

from app.models.chart import Chart, ChartSegment, ChartType
from app.models.period import Period, PeriodType
from app.models.chart_source import ChartSource, ChartMetric, SourceTable
from app.models.ad_metric import DeviceType

from app.schemas.chart import (
    ChartDataPoint,
    ChartDataPointToAnalyze,
    ChartToAnalyze,
    ChartResponse as ChartServiceChartResponse,
    PeriodResponse,
    SourceResponse,
    CompleteChart
)
from app.schemas.chat import ChatRequest, History, Role, ChatResponse, AssistantIntegration


# --- Fixtures ---
@pytest_asyncio.fixture
def mock_chart_service():
    """Mocks the ChartService dependency."""
    return AsyncMock(spec=ChartsService)

@pytest_asyncio.fixture
def mock_openai_service():
    """Mocks the OpenAIService dependency."""
    return AsyncMock(spec=OpenAIService)

@pytest_asyncio.fixture
def chat_service(mock_chart_service, mock_openai_service):
    """Provides an instance of ChatService with mocked dependencies."""
    return ChatService(
        chart_service=mock_chart_service,
        openai_service=mock_openai_service
    )

# --- Test Cases ---

@pytest.mark.asyncio
async def test_chat_initial_conversation_success(chat_service, mock_chart_service, mock_openai_service):
    """
    Testa uma conversa inicial bem-sucedida onde o histórico está vazio,
    levando à geração de instruções do sistema.
    """
    chart_id = str(uuid.uuid4())
    user_question = "Me dê uma análise inicial."
    
    mock_data_points_for_chat_service = [
        ChartDataPoint(source_id="mock_source_id_1", source_table=SourceTable.campaign, value=100, date=datetime(2023, 1, 1), device=DeviceType.desktop, metric=ChartMetric.impression),
        ChartDataPoint(source_id="mock_source_id_2", source_table=SourceTable.campaign, value=150, date=datetime(2023, 1, 2), device=None, metric=ChartMetric.impression),
        ChartDataPoint(source_id="mock_source_id_3", source_table=SourceTable.campaign, value=120, date=datetime(2023, 1, 3), device=DeviceType.mobile, metric=ChartMetric.impression),
    ]

    mock_complete_chart_obj = MagicMock(spec=CompleteChart)
    mock_complete_chart_obj.id = chart_id
    mock_complete_chart_obj.name = "Test Chart"
    mock_complete_chart_obj.type = ChartType.line
    mock_complete_chart_obj.period = PeriodResponse(type=PeriodType.day, amount=30)
    mock_complete_chart_obj.granularity = PeriodResponse(type=PeriodType.day, amount=1)
    mock_complete_chart_obj.segment = ChartSegment.date
    mock_complete_chart_obj.metric = ChartMetric.impression 
    mock_complete_chart_obj.sources = [SourceResponse(id=str(uuid.uuid4()), chart_id=chart_id, metrics=[ChartMetric.impression], source_id="mock_source", source_table=SourceTable.campaign)]


    mock_chart_response_data = ChartServiceChartResponse(
        chart=mock_complete_chart_obj,
        data=mock_data_points_for_chat_service
    )
    mock_chart_service.get_chart.return_value = mock_chart_response_data

    openai_assistant_response = "Claro! Com base nos dados de impressão, observei um pico no segundo dia."
    mock_openai_service.chat_gpt.return_value = openai_assistant_response

    chat_request = ChatRequest(
        chart_id=chart_id,
        question=user_question,
        history=[]
    )

    response = await chat_service.chat(chat_request)

    mock_chart_service.get_chart.assert_awaited_once_with(chart_id)
    mock_openai_service.chat_gpt.assert_awaited_once()

    assert isinstance(response, ChatResponse)
    assert response.response == openai_assistant_response
    assert len(response.history) == 3

    system_instructions = response.history[0]
    assert system_instructions.role == Role.system
    assert "Você é um assistente especializado em análise de dados de marketing digital." in system_instructions.content
    
    start_tag = "a seguir: \n"
    if start_tag in system_instructions.content:
        chart_to_analyze_json_str = system_instructions.content.split(start_tag)[1]
        parsed_chart_to_analyze = ChartToAnalyze.model_validate_json(chart_to_analyze_json_str)
        assert parsed_chart_to_analyze.name == mock_chart_response_data.chart.name
        assert len(parsed_chart_to_analyze.data) == len(mock_data_points_for_chat_service)
        if parsed_chart_to_analyze.data:
            assert parsed_chart_to_analyze.data[0].value == mock_data_points_for_chat_service[0].value
    else:
        pytest.fail("System instructions did not contain ChartToAnalyze JSON.")

    user_history_entry = response.history[1]
    assert user_history_entry.role == Role.user
    assert user_history_entry.content == user_question

    assistant_history_entry = response.history[2]
    assert assistant_history_entry.role == Role.assistant
    assert assistant_history_entry.content == openai_assistant_response

@pytest.mark.asyncio
async def test_chat_continuing_conversation_success(chat_service, mock_chart_service, mock_openai_service):
    """
    Testa uma conversa contínua onde o histórico não está vazio,
    garantindo que novas instruções do sistema não sejam geradas.
    """
    chart_id = str(uuid.uuid4())
    user_question = "O que você achou dos dados do terceiro dia?"
    
    existing_history = [
        History(role=Role.system, content="System initial message."),
        History(role=Role.user, content="First question."),
        History(role=Role.assistant, content="First answer.")
    ]

    mock_data_points_for_chat_service = [
        ChartDataPoint(source_id="mock_source_id_1", source_table=SourceTable.ad, value=100, date=datetime(2023, 1, 1), device=DeviceType.desktop, metric=ChartMetric.click),
        ChartDataPoint(source_id="mock_source_id_2", source_table=SourceTable.ad, value=200, date=datetime(2023, 1, 2), device=None, metric=ChartMetric.click),
    ]

    mock_complete_chart_obj = MagicMock(spec=CompleteChart)
    mock_complete_chart_obj.id = chart_id
    mock_complete_chart_obj.name = "Another Chart"
    mock_complete_chart_obj.type = ChartType.bar
    mock_complete_chart_obj.period = PeriodResponse(type=PeriodType.month, amount=6)
    mock_complete_chart_obj.granularity = PeriodResponse(type=PeriodType.week, amount=1)
    mock_complete_chart_obj.segment = ChartSegment.device
    mock_complete_chart_obj.metric = ChartMetric.click 
    mock_complete_chart_obj.sources = [SourceResponse(id=str(uuid.uuid4()), chart_id=chart_id, metrics=[ChartMetric.click], source_id="mock_source_2", source_table=SourceTable.ad)]


    mock_chart_service_response = ChartServiceChartResponse(
        chart=mock_complete_chart_obj,
        data=mock_data_points_for_chat_service
    )
    mock_chart_service.get_chart.return_value = mock_chart_service_response

    openai_assistant_response = "No terceiro dia, o valor diminuiu um pouco."
    mock_openai_service.chat_gpt.return_value = openai_assistant_response

    chat_request = ChatRequest(
        chart_id=chart_id,
        question=user_question,
        history=existing_history.copy()
    )

    response = await chat_service.chat(chat_request)

    mock_chart_service.get_chart.assert_awaited_once_with(chart_id)
    mock_openai_service.chat_gpt.assert_awaited_once()

    assert isinstance(response, ChatResponse)
    assert response.response == openai_assistant_response
    assert len(response.history) == len(existing_history) + 2

    assert response.history[0].role == Role.system
    assert response.history[0].content == "System initial message."

    user_history_entry = response.history[-2]
    assert user_history_entry.role == Role.user
    assert user_history_entry.content == user_question

    assistant_history_entry = response.history[-1]
    assert assistant_history_entry.role == Role.assistant
    assert assistant_history_entry.content == openai_assistant_response

@pytest.mark.asyncio
async def test_chat_chart_service_http_exception(chat_service, mock_chart_service, mock_openai_service):
    """
    Testa o cenário onde ChartService.get_chart levanta uma HTTPException.
    Espera que a mesma HTTPException seja re-levantada.
    """
    chart_id = str(uuid.uuid4())
    user_question = "Qual o gráfico?"
    
    mock_exception = HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chart not found")
    mock_chart_service.get_chart.side_effect = mock_exception

    chat_request = ChatRequest(
        chart_id=chart_id,
        question=user_question,
        history=[]
    )

    with pytest.raises(HTTPException) as exc_info:
        await chat_service.chat(chat_request)
    
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Chart not found"
    mock_chart_service.get_chart.assert_awaited_once_with(chart_id)
    mock_openai_service.chat_gpt.assert_not_awaited()

@pytest.mark.asyncio
async def test_chat_openai_service_exception(chat_service, mock_chart_service, mock_openai_service):
    """
    Testa o cenário onde OpenAIService.chat_gpt levanta uma exceção (não HTTP).
    Espera que uma HTTPException 502_BAD_GATEWAY seja levantada.
    """
    chart_id = str(uuid.uuid4())
    user_question = "Análise."
    
    mock_data_points_for_chat_service = [
        ChartDataPoint(source_id="mock_source_id_1", source_table=SourceTable.campaign, value=50, date=datetime(2023, 1, 1), device=DeviceType.mobile, metric=ChartMetric.spend),
    ]
    mock_complete_chart_obj = MagicMock(spec=CompleteChart)
    mock_complete_chart_obj.id = chart_id
    mock_complete_chart_obj.name = "Error Test Chart"
    mock_complete_chart_obj.type = ChartType.line
    mock_complete_chart_obj.period = PeriodResponse(type=PeriodType.day, amount=7)
    mock_complete_chart_obj.granularity = PeriodResponse(type=PeriodType.day, amount=1)
    mock_complete_chart_obj.segment = ChartSegment.date
    mock_complete_chart_obj.metric = ChartMetric.spend
    mock_complete_chart_obj.sources = [SourceResponse(id=str(uuid.uuid4()), chart_id=chart_id, metrics=[ChartMetric.spend], source_id="mock_source_err", source_table=SourceTable.campaign)]

    mock_chart_response_data = ChartServiceChartResponse(
        chart=mock_complete_chart_obj,
        data=mock_data_points_for_chat_service
    )
    mock_chart_service.get_chart.return_value = mock_chart_response_data

    mock_openai_service.chat_gpt.side_effect = Exception("OpenAI API is down")

    chat_request = ChatRequest(
        chart_id=chart_id,
        question=user_question,
        history=[]
    )
    with patch("logging.getLogger") as mock_get_logger:
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        with pytest.raises(HTTPException) as exc_info:
            await chat_service.chat(chat_request)
        
        assert exc_info.value.status_code == status.HTTP_502_BAD_GATEWAY
        assert exc_info.value.detail == "error communicating with ai service"
        mock_chart_service.get_chart.assert_awaited_once_with(chart_id)
        mock_openai_service.chat_gpt.assert_awaited_once()

        mock_logger.error.assert_called_once()
        assert "error communicating with ai service" in mock_logger.error.call_args[0][0]
        assert "OpenAI API is down" in str(mock_logger.error.call_args[0][0])
        assert mock_logger.error.call_args[1]["exc_info"] is True


@pytest.mark.asyncio
async def test_chat_empty_chart_data(chat_service, mock_chart_service, mock_openai_service):
    """
    Testa o cenário onde ChartService.get_chart retorna dados vazios.
    Garante que ChartToAnalyze.data seja uma lista vazia.
    """
    chart_id = str(uuid.uuid4())
    user_question = "Análise com dados vazios."
    
    mock_complete_chart_obj = MagicMock(spec=CompleteChart)
    mock_complete_chart_obj.id = chart_id
    mock_complete_chart_obj.name = "Empty Data Chart"
    mock_complete_chart_obj.type = ChartType.line
    mock_complete_chart_obj.period = PeriodResponse(type=PeriodType.day, amount=7)
    mock_complete_chart_obj.granularity = PeriodResponse(type=PeriodType.day, amount=1)
    mock_complete_chart_obj.segment = ChartSegment.date
    mock_complete_chart_obj.metric = ChartMetric.click
    mock_complete_chart_obj.sources = [SourceResponse(id=str(uuid.uuid4()), chart_id=chart_id, metrics=[ChartMetric.click], source_id="mock_source_empty", source_table=SourceTable.ad)]


    mock_chart_response_data = ChartServiceChartResponse(
        chart=mock_complete_chart_obj,
        data=[]
    )
    mock_chart_service.get_chart.return_value = mock_chart_response_data

    openai_assistant_response = "Não há dados disponíveis para análise."
    mock_openai_service.chat_gpt.return_value = openai_assistant_response

    chat_request = ChatRequest(
        chart_id=chart_id,
        question=user_question,
        history=[]
    )

    response = await chat_service.chat(chat_request)

    mock_chart_service.get_chart.assert_awaited_once_with(chart_id)
    mock_openai_service.chat_gpt.assert_awaited_once()

    assert isinstance(response, ChatResponse)
    assert response.response == openai_assistant_response
    assert len(response.history) == 3

    system_instructions = response.history[0]
    start_tag = "a seguir: \n"
    if start_tag in system_instructions.content:
        chart_to_analyze_json_str = system_instructions.content.split(start_tag)[1]
        parsed_chart_to_analyze = ChartToAnalyze.model_validate_json(chart_to_analyze_json_str)
        assert parsed_chart_to_analyze.data == []
    else:
        pytest.fail("System instructions did not contain ChartToAnalyze JSON for empty data test.")

    assert "Não há dados disponíveis" in openai_assistant_response


@pytest.mark.asyncio
async def test_chat_get_service(mock_chart_service, mock_openai_service):
    """Testa o método de classe get_service."""

    with patch('app.services.chat.ChartService.get_service', new_callable=AsyncMock) as mock_charts_get_service:
        with patch('app.services.chat.OpenAIService.get_service', new_callable=AsyncMock) as mock_openai_get_service:
            mock_charts_get_service.return_value = mock_chart_service
            mock_openai_get_service.return_value = mock_openai_service

            service_instance = await ChatService.get_service(
                chart_service=mock_chart_service,
                openai_service=mock_openai_service
            )

            assert isinstance(service_instance, ChatService)
            assert service_instance._ChatService__chart_service == mock_chart_service
            assert service_instance._ChatService__openai_service == mock_openai_service