from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime

from fin54.data.models import MacroRiskReport
from fin54.mcp import fred_macro
from fin54.utils.formatting import bullet_list

logger = logging.getLogger(__name__)

SERIES_MAP = {
    "inflation": ["CPI", "CORE_CPI"],
    "labor_market": ["UNEMPLOYMENT"],
    "rates_yield_curve": ["FED_FUNDS", "T10Y2Y_SPREAD"],
    "credit_stress": ["CREDIT_SPREAD"],
    "recession_indicators": ["RECESSION_PROB"],
}


def _clean_values(observations: list[dict]) -> list[float]:
    values = []
    for obs in observations:
        value = obs.get("value")
        if value not in (None, ".", ""):
            values.append(float(value))
    return values



def _analyze(series) -> str:
    values = _clean_values(series.observations)
    if not values:
        return f"{series.title}: unavailable"
    latest = values[-1]
    trailing = values[-4:] if len(values) >= 4 else values
    trend = "rising" if trailing[-1] > trailing[0] else "falling" if trailing[-1] < trailing[0] else "flat"
    average = sum(values) / len(values)
    relative = "above" if latest > average else "below" if latest < average else "in line with"
    return f"{series.title}: latest {latest:.2f}, trend {trend}, currently {relative} its sample average of {average:.2f}."


async def generate_macro_risk_report() -> MacroRiskReport:
    sections: dict[str, str] = {}
    try:
        needed = {name: fred_macro.SERIES[name] for names in SERIES_MAP.values() for name in names}
        fetched = await asyncio.gather(*[fred_macro.get_series(series_id, limit=24) for series_id in needed.values()])
        by_id = {series.series_id: series for series in fetched}
        for section_name, names in SERIES_MAP.items():
            sections[section_name] = bullet_list([_analyze(by_id[fred_macro.SERIES[name]]) for name in names])
    except Exception as exc:
        logger.warning("macro risk report generation failed: %s", exc)
        for section_name in SERIES_MAP:
            sections.setdefault(section_name, "Macro section unavailable.")
    return MacroRiskReport(date=date.today(), generated_at=datetime.now(UTC), sections=sections)
