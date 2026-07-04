from __future__ import annotations

from fin54.data.models import InsiderWatchReport, MacroRiskReport, MorningBrief, TickerReport, WhaleProxyReport
from fin54.reports.insider_watch import generate_insider_watch
from fin54.reports.macro_risk import generate_macro_risk_report
from fin54.reports.morning_brief import generate_morning_brief
from fin54.reports.ticker_report import generate_ticker_report
from fin54.reports.whale_proxy import generate_whale_proxy_report


class ReportAgent:
    async def ticker_report(self, ticker: str) -> TickerReport:
        return await generate_ticker_report(ticker)

    async def morning_brief(self) -> MorningBrief:
        return await generate_morning_brief()

    async def insider_watch(self, cik: str) -> InsiderWatchReport:
        return await generate_insider_watch(cik)

    async def macro_risk(self) -> MacroRiskReport:
        return await generate_macro_risk_report()

    async def whale_proxy(self, ticker: str) -> WhaleProxyReport:
        return await generate_whale_proxy_report(ticker)
