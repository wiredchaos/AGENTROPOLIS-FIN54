from __future__ import annotations

import logging
from datetime import UTC, date, datetime

from fin54.data.models import WhaleProxyReport
from fin54.mcp import finra_otc, market_data, sec_edgar
from fin54.utils.formatting import bullet_list, fmt_num

logger = logging.getLogger(__name__)


async def generate_whale_proxy_report(ticker: str) -> WhaleProxyReport:
    symbol = ticker.upper()
    sections = {
        "disclaimer": (
            "This report uses public, aggregated FINRA OTC weekly summary data as a loose signal proxy. "
            "It is NOT real dark pool data, not real-time, and should not be treated as direct institutional flow evidence."
        )
    }
    try:
        summary = await finra_otc.get_top_otc_volume(25)
        matched = [record for record in summary if record.ticker.upper() == symbol]
        if matched:
            sections["otc_activity"] = bullet_list(
                [f"{record.date}: {fmt_num(record.otc_volume, 0)} shares, tier={record.tier}, clearing={record.clearing_firm}" for record in matched]
            )
        else:
            sections["otc_activity"] = f"{symbol} did not appear in the sampled top OTC weekly volume list."
    except Exception as exc:
        logger.warning("whale proxy OTC section failed for %s: %s", symbol, exc)
        sections["otc_activity"] = "OTC proxy data unavailable."
    try:
        ma = market_data.get_moving_averages(symbol)
        rsi = market_data.get_rsi(symbol)
        macd = market_data.get_macd(symbol)
        sections["technical_signals"] = bullet_list(
            [
                *[f"{key.upper()}: {fmt_num(value)}" for key, value in ma.items()],
                f"RSI(14): {fmt_num(rsi)}",
                f"MACD histogram: {fmt_num(macd.get('histogram'))}",
            ]
        )
    except Exception as exc:
        logger.warning("whale proxy technical section failed for %s: %s", symbol, exc)
        sections["technical_signals"] = "Technical signals unavailable."
    try:
        matches = await sec_edgar.search_company(symbol)
        cik = str(matches[0].get("cik", "")) if matches else ""
        if cik:
            submissions = await sec_edgar.get_company_submissions(cik)
            transactions = sec_edgar.parse_insider_transactions(submissions)
            if transactions:
                sections["insider_activity"] = bullet_list(
                    [f"{tx.transaction_date}: {tx.insider_name or 'Insider'} {tx.transaction_type} {fmt_num(tx.shares, 0)} shares at {fmt_num(tx.price_per_share)}" for tx in transactions[:5]]
                )
            else:
                sections["insider_activity"] = "No recent insider activity found through SEC Form 4 metadata."
        else:
            sections["insider_activity"] = "No SEC company match found for insider lookup."
    except Exception as exc:
        logger.warning("whale proxy insider section failed for %s: %s", symbol, exc)
        sections["insider_activity"] = "Insider activity unavailable."
    return WhaleProxyReport(date=date.today(), generated_at=datetime.now(UTC), sections=sections)
