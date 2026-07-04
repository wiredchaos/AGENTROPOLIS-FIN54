"""FINRA OTC public aggregate volume module.

This module uses FINRA's public weekly OTC summary endpoint. It is delayed,
aggregated public data and is NOT a real-time dark pool feed or institutional
order-flow tape. Use it only as a loose proxy for unusual OTC activity.
"""

from __future__ import annotations

import logging

import httpx

from fin54.data.models import FinraOtcRecord

logger = logging.getLogger(__name__)

BASE_URL = "https://api.finra.org/data/group/otcMarket/name/weeklySummary"
DISCLAIMER = "Public aggregated FINRA OTC volume only; not real-time dark pool data."


async def get_otc_weekly_summary(limit: int = 20) -> list[FinraOtcRecord]:
    params = {"limit": limit}
    headers = {"Accept": "application/json"}
    try:
        async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
            response = await client.get(BASE_URL, params=params)
            response.raise_for_status()
            payload = response.json()
    except Exception as exc:
        logger.warning("FINRA OTC request failed: %s", exc)
        return []
    if not isinstance(payload, list):
        logger.warning("FINRA OTC response format changed")
        return []
    records: list[FinraOtcRecord] = []
    for row in payload:
        try:
            records.append(
                FinraOtcRecord(
                    ticker=str(row.get("issueSymbolIdentifier") or row.get("symbolCode") or row.get("ticker") or "UNKNOWN"),
                    date=str(row.get("weekStartDate") or row.get("tradeReportDate") or row.get("date") or ""),
                    otc_volume=float(row.get("totalWeeklyShareQuantity") or row.get("shareQuantity") or row.get("otc_volume") or 0.0),
                    tier=str(row.get("tierIdentifier") or row.get("marketClassCode") or DISCLAIMER),
                    clearing_firm=str(row.get("marketParticipantName") or row.get("clearingFirm") or DISCLAIMER),
                )
            )
        except Exception as exc:
            logger.warning("failed to parse FINRA row: %s", exc)
    return records


async def get_top_otc_volume(n: int = 10) -> list[FinraOtcRecord]:
    records = await get_otc_weekly_summary(limit=max(n, 20))
    return sorted(records, key=lambda item: item.otc_volume, reverse=True)[:n]
