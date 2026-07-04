import asyncio
from unittest.mock import AsyncMock, patch

from fin54.mcp.fred_macro import SERIES, get_series


class MockResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


def test_get_series_returns_macroseries():
    observations_payload = {"observations": [{"date": "2024-01-01", "value": "3.1"}]}
    info_payload = {"seriess": [{"title": "Consumer Price Index", "units": "Index", "frequency": "Monthly"}]}
    with patch("httpx.AsyncClient.get", new=AsyncMock(side_effect=[MockResponse(observations_payload), MockResponse(info_payload)])):
        series = asyncio.run(get_series("CPIAUCSL", limit=1))
    assert series.series_id == "CPIAUCSL"
    assert series.title == "Consumer Price Index"
    assert series.observations[0]["value"] == "3.1"


def test_series_dict_has_expected_keys():
    assert {"CPI", "UNEMPLOYMENT", "VIX", "T10Y2Y_SPREAD"}.issubset(SERIES.keys())
