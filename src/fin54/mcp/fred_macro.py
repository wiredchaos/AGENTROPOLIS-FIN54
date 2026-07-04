from __future__ import annotations

import logging

import httpx

from fin54.data.models import MacroSeries
from fin54.utils.config import FRED_API_KEY

logger = logging.getLogger(__name__)

BASE_URL = "https://api.stlouisfed.org/fred"
SERIES = {
    "CPI": "CPIAUCSL",
    "CORE_CPI": "CPILFESL",
    "UNEMPLOYMENT": "UNRATE",
    "FED_FUNDS": "DFF",
    "T10Y": "DGS10",
    "T2Y": "DGS2",
    "T10Y2Y_SPREAD": "T10Y2Y",
    "GDP": "GDP",
    "M2": "M2SL",
    "CREDIT_SPREAD": "BAA10Y",
    "RECESSION_PROB": "RECPROUSM156N",
    "VIX": "VIXCLS",
}


async def get_series_info(series_id: str) -> dict:
    params = {"api_key": FRED_API_KEY, "series_id": series_id, "file_type": "json"}
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/series", params=params)
        response.raise_for_status()
        return response.json()


async def get_series(series_id: str, limit: int = 100) -> MacroSeries:
    params = {
        "api_key": FRED_API_KEY,
        "series_id": series_id,
        "limit": limit,
        "file_type": "json",
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(f"{BASE_URL}/series/observations", params=params)
        response.raise_for_status()
        observations_payload = response.json()
    title = series_id
    units = ""
    frequency = ""
    try:
        info_payload = await get_series_info(series_id)
        info = (info_payload.get("seriess") or [{}])[0]
        title = info.get("title", title)
        units = info.get("units", "")
        frequency = info.get("frequency", "")
    except Exception as exc:  # pragma: no cover
        logger.warning("failed to fetch FRED series info for %s: %s", series_id, exc)
    return MacroSeries(
        series_id=series_id,
        title=title,
        units=units,
        frequency=frequency,
        observations=observations_payload.get("observations", []),
    )
