from __future__ import annotations

import logging
import math
from datetime import UTC, datetime

from fin54.data.models import TickerReport
from fin54.mcp import market_data, news_sentiment
from fin54.utils.formatting import bullet_list, fmt_num, fmt_pct

logger = logging.getLogger(__name__)


async def generate_ticker_report(ticker: str) -> TickerReport:
    sections: dict[str, str] = {}
    symbol = ticker.upper()
    try:
        quote = market_data.get_quote(symbol)
        averages = market_data.get_moving_averages(symbol)
        rsi = market_data.get_rsi(symbol)
        macd = market_data.get_macd(symbol)
        volatility = market_data.get_volatility(symbol)
        sections["overview"] = bullet_list(
            [
                f"Ticker: {symbol}",
                f"Last price: {fmt_num(quote.get('price'))}",
                f"Daily change: {fmt_num(quote.get('change'))} ({fmt_pct(quote.get('change_pct'))})",
                f"Volume: {fmt_num(quote.get('volume'), 0)}",
            ]
        )
        sections["technicals"] = bullet_list(
            [
                *[f"{name.upper()}: {fmt_num(value)}" for name, value in averages.items()],
                f"RSI(14): {fmt_num(rsi)}",
                f"MACD: {fmt_num(macd.get('macd'))} / Signal: {fmt_num(macd.get('signal'))} / Histogram: {fmt_num(macd.get('histogram'))}",
                f"30-day annualized volatility: {fmt_pct(None if math.isnan(volatility) else volatility * 100)}",
            ]
        )
    except Exception as exc:
        logger.warning("ticker technical report failed for %s: %s", symbol, exc)
        sections["overview"] = f"Technical overview for {symbol} is temporarily unavailable."
        sections.setdefault("technicals", sections["overview"])
    try:
        items = news_sentiment.fetch_ticker_news(symbol)
        sections["news_sentiment"] = "\n\n".join(
            [news_sentiment.summarize_ticker_narrative(symbol, items), bullet_list([f"{item.source}: {item.title} ({item.sentiment})" for item in items[:5]])]
        )
    except Exception as exc:
        logger.warning("ticker news report failed for %s: %s", symbol, exc)
        sections["news_sentiment"] = f"News and sentiment for {symbol} could not be assembled."
    return TickerReport(ticker=symbol, generated_at=datetime.now(UTC), sections=sections)
