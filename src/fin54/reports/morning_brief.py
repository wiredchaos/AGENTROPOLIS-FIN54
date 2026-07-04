from __future__ import annotations

import asyncio
import logging
from datetime import UTC, date, datetime

from fin54.data.models import MorningBrief
from fin54.mcp import fred_macro, market_data, news_sentiment
from fin54.utils.formatting import bullet_list, fmt_num

logger = logging.getLogger(__name__)

BENCHMARKS = ["SPY", "QQQ", "IWM", "DXY=X", "GC=F", "CL=F"]
SERIES_KEYS = ["FED_FUNDS", "T10Y2Y_SPREAD", "UNEMPLOYMENT", "VIX"]


def _latest_value(series) -> str:
    for obs in reversed(series.observations):
        value = obs.get("value")
        if value not in (None, ".", ""):
            return str(value)
    return "n/a"


async def generate_morning_brief() -> MorningBrief:
    sections: dict[str, str] = {}
    try:
        macro_series = await asyncio.gather(*[fred_macro.get_series(fred_macro.SERIES[key], limit=12) for key in SERIES_KEYS])
        sections["macro_snapshot"] = bullet_list(
            [f"{name.replace('_', ' ').title()}: {_latest_value(series)}" for name, series in zip(SERIES_KEYS, macro_series)]
        )
    except Exception as exc:
        logger.warning("morning brief macro section failed: %s", exc)
        sections["macro_snapshot"] = "Macro snapshot unavailable."
    try:
        sections["market_overview"] = bullet_list(
            [
                f"{ticker}: {fmt_num(quote['price'])} ({fmt_num(quote['change'])}, {quote['change_pct']:.2f}%)"
                for ticker, quote in ((ticker, market_data.get_quote(ticker)) for ticker in BENCHMARKS)
            ]
        )
    except Exception as exc:
        logger.warning("morning brief market section failed: %s", exc)
        sections["market_overview"] = "Benchmark market overview unavailable."
    try:
        market_news = news_sentiment.fetch_market_news(max_items=8)
        sections["news_highlights"] = bullet_list([f"{item.source}: {item.title} ({item.sentiment})" for item in market_news[:8]])
    except Exception as exc:
        logger.warning("morning brief news section failed: %s", exc)
        sections["news_highlights"] = "Market news highlights unavailable."
    return MorningBrief(date=date.today(), generated_at=datetime.now(UTC), sections=sections)
