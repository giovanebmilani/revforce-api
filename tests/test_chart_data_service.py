import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone

from app.models.ad_metric import DeviceType
from app.schemas.chart import PeriodSchema, ChartDataPoint
from app.models.chart_source import SourceTable, ChartMetric
from app.models.chart import ChartSegment
from app.models.period import PeriodType
from app.services.chart_data import DataService

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result


@pytest.mark.asyncio
async def test_get_for_source_and_metric_ad_with_clicks():
    # Setup
    mock_session = AsyncMock(spec=AsyncSession)

    # Data to be returned from DB
    now = datetime.now(timezone.utc)
    sample_metric = MagicMock()
    sample_metric.date = now
    sample_metric.device = DeviceType.mobile
    mock_value = 42

    # Mocking result of scalar call
    mock_session.scalar.return_value = now

    # Mocking result of execute call
    mock_result = MagicMock(spec=Result)
    mock_result.all.return_value = [(sample_metric, mock_value)]
    mock_session.execute.return_value = mock_result

    service = DataService(mock_session)

    # Act
    result = await service.get_for_source_and_metric(
        source_table=SourceTable.ad,
        source_id="ad123",
        period=PeriodSchema(type=PeriodType.day, amount=7),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        metric=ChartMetric.click,
        segment=None  # substituído ChartSegment.none por None
    )

    # Assert
    assert len(result) == 1
    dp = result[0]
    assert dp.source_id == "ad123"
    assert dp.metric == ChartMetric.click
    assert dp.value == 42
    assert dp.device is None  # segment != device => group_by_device

@pytest.mark.asyncio
async def test_get_for_source_and_metric_campaign_no_data():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.scalar.return_value = None  # No start_time found

    service = DataService(mock_session)

    result = await service.get_for_source_and_metric(
        source_table=SourceTable.campaign,
        source_id="camp456",
        period=PeriodSchema(type=PeriodType.week, amount=1),
        granularity=PeriodSchema(type=PeriodType.day, amount=1),
        metric=ChartMetric.impression,
        segment=ChartSegment.device
    )

    assert result == []

@pytest.mark.asyncio
async def test_get_for_source_multiple_metrics():
    mock_session = AsyncMock(spec=AsyncSession)
    now = datetime.now(timezone.utc)

    # Simula que existem dados
    mock_session.scalar.return_value = now

    # Simula resultado para dois diferentes tipos de métrica
    result_data = MagicMock()
    result_data.date = now
    result_data.device = DeviceType.desktop

    result_obj = MagicMock()
    result_obj.all.return_value = [(result_data, 100)]

    mock_session.execute.return_value = result_obj

    service = DataService(mock_session)

    result = await service.get_for_source(
        source_table=SourceTable.ad,
        source_id="adX",
        period=PeriodSchema(type=PeriodType.hour, amount=2),
        granularity=PeriodSchema(type=PeriodType.hour, amount=1),
        metrics=[ChartMetric.click, ChartMetric.spend],
        segment=None,  # substituído ChartSegment.none por None
    )

    assert len(result) == 2
    for dp in result:
        assert dp.device is None
        assert dp.source_id == "adX"


@pytest.mark.asyncio
async def test_get_for_chart_runs_all_sources():
    mock_session = AsyncMock(spec=AsyncSession)
    now = datetime.now(timezone.utc)
    mock_session.scalar.return_value = now

    result_data = MagicMock()
    result_data.date = now
    result_data.device = DeviceType.desktop
    mock_result = MagicMock()
    mock_result.all.return_value = [(result_data, 10)]
    mock_session.execute.return_value = mock_result

    service = DataService(mock_session)

    class DummySource:
        source_id = "abc"
        source_table = SourceTable.ad
        metrics = [ChartMetric.click]

    chart = MagicMock()
    chart.sources = [DummySource(), DummySource()]
    chart.period = PeriodSchema(type=PeriodType.day, amount=1)
    chart.granularity = PeriodSchema(type=PeriodType.day, amount=1)
    chart.segment = None  # substituído ChartSegment.none por None

    result = await service.get_for_chart(chart)
    assert len(result) == 2