import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch, call
import sys
import os
import uuid
from datetime import datetime

from fastapi import HTTPException
from starlette import status

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.charts import ChartService 
from app.models.chart import Chart, ChartSegment, ChartType
from app.models.period import Period, PeriodType
from app.models.chart_source import ChartSource, ChartMetric, SourceTable
from app.models.ad_metric import DeviceType

from app.schemas.chart import (
    ChartRequest,
    ChartResponse,
    UpdateChartOrderRequest,
    PeriodSchema,
    SourceSchema,
    CompleteChart,
    ChartDataPoint,
    PeriodResponse,
    SourceResponse
)

# --- Fixtures ---
@pytest_asyncio.fixture
def mock_chart_repository():
    return AsyncMock()

@pytest_asyncio.fixture
def mock_period_repository():
    return AsyncMock()

@pytest_asyncio.fixture
def mock_chart_source_repository():
    return AsyncMock()

@pytest_asyncio.fixture
def mock_account_service():
    return AsyncMock()

@pytest_asyncio.fixture
def mock_data_service():
    return AsyncMock()

@pytest_asyncio.fixture
def service(
    mock_chart_repository,
    mock_period_repository,
    mock_chart_source_repository,
    mock_account_service,
    mock_data_service,
):
    return ChartService(
        chart_repository=mock_chart_repository,
        period_repository=mock_period_repository,
        chart_source_repository=mock_chart_source_repository,
        account_service=mock_account_service,
        data_service=mock_data_service,
    )

async def _make_mock_chart_response_object(chart: Chart, data_points: list[ChartDataPoint]) -> ChartResponse:
    chart_period_response = PeriodResponse(type=chart.period.type, amount=chart.period.amount)
    chart_granularity_response = PeriodResponse(type=chart.granularity.type, amount=chart.granularity.amount)

    chart_sources_response = []
    for s in chart.sources:
        source_id_val = getattr(s, 'id', str(uuid.uuid4()))
        chart_sources_response.append(SourceResponse(
            id=source_id_val,
            chart_id=s.chart_id,
            metrics=s.metrics,
            source_id=s.source_id,
            source_table=s.source_table,
        ))

    return ChartResponse(
        chart=CompleteChart(
            id=chart.id,
            name=chart.name,
            position=chart.position,
            type=chart.type,
            period=chart_period_response,
            granularity=chart_granularity_response,
            sources=chart_sources_response,
            segment=chart.segment,
        ),
        data=data_points,
    )

# --- Testes ---

@pytest.mark.asyncio
async def test_get_chart_success(service, mock_chart_repository, mock_data_service):
    """Testa a recuperação bem-sucedida de um gráfico."""
    chart_id = str(uuid.uuid4())
    mock_period = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=7)
    mock_granularity = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=1)
    mock_sources = [
        ChartSource(
            id=str(uuid.uuid4()),
            chart_id=chart_id,
            metrics=[ChartMetric.click],
            source_id="s1",
            source_table=SourceTable.ad
        )
    ]
    mock_chart = Chart(
        id=chart_id,
        account_id="acc123",
        name="Test Chart",
        position=1,
        type=ChartType.line,
        period_id=mock_period.id,
        granularity_id=mock_granularity.id,
        segment=ChartSegment.date,
        period=mock_period,
        granularity=mock_granularity,
        sources=mock_sources
    )
    mock_chart_repository.get.return_value = mock_chart

    mock_data_points_for_chart = [
        ChartDataPoint(
            source_id="s1_data",
            source_table=SourceTable.ad,
            value=100,
            date=datetime(2025, 6, 15, 10, 0, 0),
            metric=ChartMetric.click,
            device=DeviceType.desktop
        )
    ]
    mock_data_service.get_for_chart.return_value = mock_data_points_for_chart

    with patch.object(service, '_make_chart_response', new_callable=AsyncMock) as mock_make_chart_response_method:
        expected_chart_response = await _make_mock_chart_response_object(mock_chart, mock_data_points_for_chart)
        mock_make_chart_response_method.return_value = expected_chart_response

        result = await service.get_chart(chart_id)

        mock_chart_repository.get.assert_awaited_once_with(chart_id)
        mock_make_chart_response_method.assert_awaited_once_with(mock_chart)
        assert isinstance(result, ChartResponse)
        assert result.chart.id == chart_id
        assert result.data == expected_chart_response.data


@pytest.mark.asyncio
async def test_get_chart_not_found(service, mock_chart_repository):
    """Testa a recuperação de um gráfico inexistente, esperando um 404."""

    chart_id = str(uuid.uuid4())
    mock_chart_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.get_chart(chart_id)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Chart not found."
    mock_chart_repository.get.assert_awaited_once_with(chart_id)

@pytest.mark.asyncio
async def test_list_charts_success(service, mock_chart_repository, mock_data_service):
    """Testa a listagem bem-sucedida de gráficos para uma determinada conta."""

    account_id = "acc123"
    mock_period_1 = Period(id=str(uuid.uuid4()), type=PeriodType.month, amount=3)
    mock_granularity_1 = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=1)
    mock_chart_1 = Chart(
        id=str(uuid.uuid4()),
        account_id=account_id,
        name="Chart 1",
        position=1,
        type=ChartType.bar,
        period_id=mock_period_1.id,
        granularity_id=mock_granularity_1.id,
        segment=ChartSegment.date,
        period=mock_period_1,
        granularity=mock_granularity_1,
        sources=[]
    )
    mock_period_2 = Period(id=str(uuid.uuid4()), type=PeriodType.month, amount=12)
    mock_granularity_2 = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=7)
    mock_chart_2 = Chart(
        id=str(uuid.uuid4()),
        account_id=account_id,
        name="Chart 2",
        position=2,
        type=ChartType.bar,
        period_id=mock_period_2.id,
        granularity_id=mock_granularity_2.id,
        segment=ChartSegment.date,
        period=mock_period_2,
        granularity=mock_granularity_2,
        sources=[]
    )
    mock_chart_repository.list.return_value = [mock_chart_1, mock_chart_2]

    mock_data_points_1 = [
        ChartDataPoint(source_id="s1_c1", source_table=SourceTable.ad, value=10, date=datetime(2025, 6, 15, 11, 0, 0), metric=ChartMetric.click, device=DeviceType.desktop)
    ]
    mock_data_points_2 = [
        ChartDataPoint(source_id="s1_c2", source_table=SourceTable.crm, value=20, date=datetime(2025, 6, 15, 12, 0, 0), metric=ChartMetric.spend, device=DeviceType.mobile)
    ]

    with patch.object(service, '_make_chart_response', new_callable=AsyncMock) as mock_make_chart_response_method:
        mock_data_service.get_for_chart.side_effect = [mock_data_points_1, mock_data_points_2]

        mock_make_chart_response_method.side_effect = [
            await _make_mock_chart_response_object(mock_chart_1, mock_data_points_1),
            await _make_mock_chart_response_object(mock_chart_2, mock_data_points_2)
        ]

        results = await service.list_charts(account_id)

        mock_chart_repository.list.assert_awaited_once_with(account_id)
        assert mock_make_chart_response_method.call_count == 2
        assert len(results) == 2
        assert isinstance(results[0], ChartResponse)
        assert results[0].chart.name == "Chart 1"
        assert results[0].data == mock_data_points_1
        assert isinstance(results[1], ChartResponse)
        assert results[1].chart.name == "Chart 2"
        assert results[1].data == mock_data_points_2


@pytest.mark.asyncio
async def test_create_chart_success(
    service,
    mock_chart_repository,
    mock_period_repository,
    mock_chart_source_repository,
    mock_account_service
):
    """Testa a criação bem-sucedida de um novo gráfico."""

    account_id = "acc123"
    chart_req = ChartRequest(
        account_id=account_id,
        name="New Chart",
        position=None,
        type=ChartType.line,
        period=PeriodSchema(type=PeriodType.day, amount=30),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        segment=ChartSegment.date,
        sources=[SourceSchema(metrics=[ChartMetric.click], source_id="s_abc", source_table=SourceTable.ad)]
    )

    mock_account_service.get_account.return_value = {"id": account_id}
    mock_chart_repository.get_by_name.return_value = None
    mock_chart_repository.list.return_value = [
        MagicMock(position=1), MagicMock(position=2)
    ]

    mock_period_repo_period = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=30)
    mock_period_repo_granularity = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=1)
    mock_period_repository.create.side_effect = [mock_period_repo_period, mock_period_repo_granularity]

    mock_created_chart = Chart(
        id=str(uuid.uuid4()),
        account_id=account_id,
        name="New Chart",
        position=3,
        type=ChartType.line,
        period_id=mock_period_repo_period.id,
        granularity_id=mock_period_repo_granularity.id,
        segment=ChartSegment.date,
    )
    mock_chart_repository.create.return_value = mock_created_chart
    mock_chart_source_repository.create.return_value = MagicMock()

    result = await service.create_chart(chart_req)

    mock_account_service.get_account.assert_awaited_once_with(account_id)
    mock_chart_repository.get_by_name.assert_awaited_once_with("New Chart")
    mock_chart_repository.list.assert_awaited_once_with(account_id)
    assert mock_period_repository.create.call_count == 2
    mock_chart_repository.create.assert_awaited_once()
    mock_chart_source_repository.create.assert_awaited_once()
    assert result == mock_created_chart
    assert result.position == 3

@pytest.mark.asyncio
async def test_create_chart_account_not_found(service, mock_account_service):
    """Testa a criação de gráficos quando a conta associada não existe."""

    chart_req = ChartRequest(
        account_id="non_existent",
        name="New Chart",
        position=1,
        type=ChartType.line,
        period=PeriodSchema(type=PeriodType.day, amount=30),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        segment=ChartSegment.date,
        sources=[]
    )
    mock_account_service.get_account.side_effect = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Account not found."
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_chart(chart_req)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Account not found."
    mock_account_service.get_account.assert_awaited_once_with("non_existent")

@pytest.mark.asyncio
async def test_create_chart_name_conflict(service, mock_chart_repository, mock_account_service):
    """Testa a criação de gráficos com um nome que já existe."""

    account_id = "acc123"
    chart_req = ChartRequest(
        account_id=account_id,
        name="Existing Chart",
        position=1,
        type=ChartType.line,
        period=PeriodSchema(type=PeriodType.day, amount=30),
        granularity=PeriodSchema(type=PeriodType.day, amount=1), 
        segment=ChartSegment.date,
        sources=[]
    )
    mock_account_service.get_account.return_value = {"id": account_id}
    mock_chart_repository.get_by_name.return_value = Chart(
        id=str(uuid.uuid4()), account_id=account_id, name="Existing Chart", position=1, type=ChartType.line, period_id="", granularity_id="", segment=ChartSegment.date
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.create_chart(chart_req)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Chart with name already exists"
    mock_chart_repository.get_by_name.assert_awaited_once_with("Existing Chart")

@pytest.mark.asyncio
async def test_create_chart_position_conflict(service, mock_chart_repository, mock_account_service):
    """Testa a criação de gráficos com uma posição que já está ocupada."""

    account_id = "acc123"
    chart_req = ChartRequest(
        account_id=account_id,
        name="New Chart",
        position=1,
        type=ChartType.line,
        period=PeriodSchema(type=PeriodType.day, amount=30),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        segment=ChartSegment.date,
        sources=[]
    )
    mock_account_service.get_account.return_value = {"id": account_id}
    mock_chart_repository.get_by_name.return_value = None
    mock_chart_repository.list.return_value = [
        MagicMock(position=1), MagicMock(position=2)
    ]

    with pytest.raises(HTTPException) as exc_info:
        await service.create_chart(chart_req)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "You already have a chart on position 1"
    mock_chart_repository.list.assert_awaited_once_with(account_id)


@pytest.mark.asyncio
async def test_delete_chart_success(service, mock_chart_repository):
    """Testa a exclusão bem-sucedida de um gráfico."""

    chart_id = str(uuid.uuid4())
    mock_chart_repository.delete.return_value = None

    await service.delete_chart(chart_id)

    mock_chart_repository.delete.assert_awaited_once_with(chart_id)

@pytest.mark.asyncio
async def test_update_chart_success(
    service,
    mock_chart_repository,
    mock_period_repository,
    mock_chart_source_repository
):
    """Testa a atualização bem-sucedida de um gráfico existente."""

    chart_id = str(uuid.uuid4())
    existing_period_id = str(uuid.uuid4())
    existing_granularity_id = str(uuid.uuid4())
    existing_chart = Chart(
        id=chart_id,
        account_id="acc123",
        name="Old Name",
        position=1,
        type=ChartType.line,
        period_id=existing_period_id,
        granularity_id=existing_granularity_id,
        segment=ChartSegment.date,
        period=Period(id=existing_period_id, type=PeriodType.day, amount=30),
        granularity=Period(id=existing_granularity_id, type=PeriodType.day, amount=1),
        sources=[]
    )

    chart_req = ChartRequest(
        account_id="acc123",
        name="Updated Name",
        position=2,
        type=ChartType.bar,
        period=PeriodSchema(type=PeriodType.month, amount=6),
        granularity=PeriodSchema(type=PeriodType.day, amount=7),
        segment=ChartSegment.date,
        sources=[SourceSchema(metrics=[ChartMetric.impression], source_id="s_xyz", source_table=SourceTable.ad)]
    )

    mock_chart_repository.get.return_value = existing_chart
    mock_chart_repository.get_by_name.return_value = None 
    mock_chart_repository.list.return_value = [
        MagicMock(id="other_chart", position=3)
    ]

    updated_period_obj_for_mock_return = Period(id=existing_period_id, type=PeriodType.month, amount=6)
    updated_granularity_obj_for_mock_return = Period(id=existing_granularity_id, type=PeriodType.day, amount=7)

    mock_period_repository.update.side_effect = [
        updated_period_obj_for_mock_return,
        updated_granularity_obj_for_mock_return
    ]
    mock_chart_repository.update.return_value = existing_chart
    mock_chart_source_repository.delete_by_chart_id.return_value = None
    mock_chart_source_repository.create.return_value = MagicMock()

    updated_chart_result = await service.update_chart(chart_id, chart_req)

    mock_chart_repository.get.assert_awaited_once_with(chart_id)
    mock_chart_repository.get_by_name.assert_awaited_once_with("Updated Name")
    mock_chart_repository.list.assert_awaited_once_with("acc123")
    assert mock_period_repository.update.call_count == 2
    
    assert any(
        call_args.args[0] == existing_period_id and
        isinstance(call_args.args[1], Period) and
        call_args.args[1].type == PeriodType.month and
        call_args.args[1].amount == 6
        for call_args in mock_period_repository.update.call_args_list
    ), "Call to update period_id with correct Period object not found"

    assert any(
        call_args.args[0] == existing_granularity_id and
        isinstance(call_args.args[1], Period) and
        call_args.args[1].type == PeriodType.day and
        call_args.args[1].amount == 7
        for call_args in mock_period_repository.update.call_args_list
    ), "Call to update granularity_id with correct Period object not found"


    mock_chart_repository.update.assert_awaited_once()
    updated_chart_arg = mock_chart_repository.update.call_args[0][0]
    assert updated_chart_arg.id == chart_id
    assert updated_chart_arg.name == "Updated Name"
    assert updated_chart_arg.position == 2
    assert updated_chart_arg.type == ChartType.bar
    assert updated_chart_arg.segment == ChartSegment.date

    mock_chart_source_repository.delete_by_chart_id.assert_awaited_once_with(chart_id)
    mock_chart_source_repository.create.assert_awaited_once()
    assert updated_chart_result == existing_chart

@pytest.mark.asyncio
async def test_update_chart_not_found(service, mock_chart_repository):
    """Testa a atualização de um gráfico inexistente, esperando um 404."""

    chart_id = str(uuid.uuid4())
    chart_req = ChartRequest(
        account_id="acc123", name="New Name", position=1, type=ChartType.line,
        period=PeriodSchema(type=PeriodType.day, amount=1),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        segment=ChartSegment.date,
        sources=[]
    )
    mock_chart_repository.get.return_value = None

    with pytest.raises(HTTPException) as exc_info:
        await service.update_chart(chart_id, chart_req)
    assert exc_info.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc_info.value.detail == "Chart not found."
    mock_chart_repository.get.assert_awaited_once_with(chart_id)

@pytest.mark.asyncio
async def test_update_chart_name_conflict(service, mock_chart_repository):
    """Testa a atualização de um gráfico com um nome que conflita com outro gráfico."""

    chart_id = str(uuid.uuid4())
    existing_chart = Chart(
        id=chart_id, account_id="acc123", name="Original Name", position=1, type=ChartType.line, period_id="", granularity_id="", segment=ChartSegment.date
    )
    conflicting_chart = Chart(
        id=str(uuid.uuid4()), account_id="acc123", name="Conflicting Name", position=2, type=ChartType.line, period_id="", granularity_id="", segment=ChartSegment.date
    )
    chart_req = ChartRequest(
        account_id="acc123", name="Conflicting Name", position=1, type=ChartType.line,
        period=PeriodSchema(type=PeriodType.day, amount=1),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        segment=ChartSegment.date,
        sources=[]
    )

    mock_chart_repository.get.return_value = existing_chart
    mock_chart_repository.get_by_name.return_value = conflicting_chart

    with pytest.raises(HTTPException) as exc_info:
        await service.update_chart(chart_id, chart_req)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "Chart with name already exists"
    mock_chart_repository.get.assert_awaited_once_with(chart_id)
    mock_chart_repository.get_by_name.assert_awaited_once_with("Conflicting Name")

@pytest.mark.asyncio
async def test_update_chart_position_conflict(service, mock_chart_repository):
    """Testa a atualização de um gráfico para uma posição que já está ocupada por outro."""

    chart_id = str(uuid.uuid4())
    existing_chart = Chart(
        id=chart_id, account_id="acc123", name="Original Name", position=1, type=ChartType.line, period_id="", granularity_id="", segment=ChartSegment.date
    )
    chart_req = ChartRequest(
        account_id="acc123", name="New Name", position=2, type=ChartType.line,
        period=PeriodSchema(type=PeriodType.day, amount=1),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        segment=ChartSegment.date,
        sources=[]
    )

    mock_chart_repository.get.return_value = existing_chart
    mock_chart_repository.get_by_name.return_value = None
    mock_chart_repository.list.return_value = [
        MagicMock(id="other_chart_1", position=2),
        MagicMock(id=chart_id, position=1)
    ]

    with pytest.raises(HTTPException) as exc_info:
        await service.update_chart(chart_id, chart_req)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "You already have a chart on position 2"
    mock_chart_repository.list.assert_awaited_once_with("acc123")

@pytest.mark.asyncio
async def test_update_order_success(service, mock_chart_repository):
    """Testa a atualização bem-sucedida da ordem/posições do gráfico."""

    account_id = "acc123"
    new_positions = {"chart1": 3, "chart2": 1, "chart3": 2}
    update_order_req = UpdateChartOrderRequest(positions=new_positions)

    mock_chart1 = Chart(id="chart1", account_id=account_id, name="Chart A", position=1, type=ChartType.line, period_id=str(uuid.uuid4()), granularity_id=str(uuid.uuid4()), segment=ChartSegment.date)
    mock_chart2 = Chart(id="chart2", account_id=account_id, name="Chart B", position=2, type=ChartType.line, period_id=str(uuid.uuid4()), granularity_id=str(uuid.uuid4()), segment=ChartSegment.date)
    mock_chart3 = Chart(id="chart3", account_id=account_id, name="Chart C", position=3, type=ChartType.line, period_id=str(uuid.uuid4()), granularity_id=str(uuid.uuid4()), segment=ChartSegment.date)

    mock_charts = [mock_chart1, mock_chart2, mock_chart3]
    mock_chart_repository.list.return_value = mock_charts

    async def mock_bulk_update_positions_side_effect(charts_to_update):
        for chart in charts_to_update:
            if chart.id in new_positions:
                chart.position = new_positions[chart.id]
    mock_chart_repository.bulk_update_positions.side_effect = mock_bulk_update_positions_side_effect

    result = await service.update_order(account_id, update_order_req)

    mock_chart_repository.list.assert_awaited_once_with(account_id)
    mock_chart_repository.bulk_update_positions.assert_awaited_once_with(mock_charts)

    assert result == {"detail": "Positions updated"}

    assert mock_chart1.position == 3
    assert mock_chart2.position == 1
    assert mock_chart3.position == 2


@pytest.mark.asyncio
async def test_update_order_position_conflict(service, mock_chart_repository):
    """Testa a atualização da ordem do gráfico com posições conflitantes."""

    account_id = "acc123"
    new_positions = {"chart1": 1, "chart2": 1}
    update_order_req = UpdateChartOrderRequest(positions=new_positions)

    mock_charts = [
        Chart(id="chart1", account_id=account_id, name="C1", position=5, type=ChartType.line, period_id=str(uuid.uuid4()), granularity_id=str(uuid.uuid4()), segment=ChartSegment.date),
        Chart(id="chart2", account_id=account_id, name="C2", position=6, type=ChartType.line, period_id=str(uuid.uuid4()), granularity_id=str(uuid.uuid4()), segment=ChartSegment.date),
    ]
    mock_chart_repository.list.return_value = mock_charts

    with pytest.raises(HTTPException) as exc_info:
        await service.update_order(account_id, update_order_req)
    assert exc_info.value.status_code == status.HTTP_409_CONFLICT
    assert exc_info.value.detail == "You have charts in the same position"
    mock_chart_repository.list.assert_awaited_once_with(account_id)
    mock_chart_repository.bulk_update_positions.assert_not_awaited()

@pytest.mark.asyncio
async def test_get_chart_position_by_account(service, mock_chart_repository):
    """Testa a recuperação das posições do gráfico por ID da conta."""

    account_id = "acc123"
    mock_positions = {"chart1": 1, "chart2": 2}
    mock_chart_repository.get_chart_position_by_account.return_value = mock_positions

    result = await service.get_chart_position_by_account(account_id)

    mock_chart_repository.get_chart_position_by_account.assert_awaited_once_with(account_id)
    assert result == mock_positions

@pytest.mark.asyncio
async def test_make_chart_response(service, mock_data_service):
    """Testa o método auxiliar privado _make_chart_response."""

    chart_id = str(uuid.uuid4())
    mock_period = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=7)
    mock_granularity = Period(id=str(uuid.uuid4()), type=PeriodType.day, amount=1)
    mock_source = ChartSource(
        id=str(uuid.uuid4()),
        chart_id=chart_id,
        metrics=[ChartMetric.click],
        source_id="s_mock",
        source_table=SourceTable.ad
    )
    mock_chart = Chart(
        id=chart_id,
        account_id="acc123",
        name="Test Chart",
        position=1,
        type=ChartType.line,
        period_id=mock_period.id,
        granularity_id=mock_granularity.id,
        segment=ChartSegment.date,
        period=mock_period,
        granularity=mock_granularity,
        sources=[mock_source]
    )

    mock_data_points = [
        ChartDataPoint(
            source_id="mock_source_id_data",
            source_table=SourceTable.ad,
            value=100,
            date=datetime(2025, 6, 15, 13, 0, 0),
            metric=ChartMetric.click,
            device=DeviceType.desktop
        )
    ]
    mock_data_service.get_for_chart.return_value = mock_data_points

    response = await service._make_chart_response(mock_chart)

    mock_data_service.get_for_chart.assert_awaited_once_with(mock_chart)
    assert isinstance(response, ChartResponse)
    assert response.chart.id == chart_id
    assert response.chart.name == "Test Chart"
    assert response.chart.period.type == PeriodType.day
    assert response.chart.granularity.type == PeriodType.day
    assert response.chart.sources[0].metrics == [ChartMetric.click]
    assert response.data == mock_data_points