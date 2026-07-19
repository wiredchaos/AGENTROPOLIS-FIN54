"""Native Model Context Protocol server for FIN54.

The REST gateway remains available in ``fin54.mcp.server``. This module exposes
FIN54's read-only financial intelligence functions as MCP tools over stdio.
"""

from __future__ import annotations

import json
from typing import Any

from mcp.server.fastmcp import FastMCP

from fin54.mcp import finra_otc, fred_macro, market_data, news_sentiment, sec_edgar
from fin54.reports.insider_watch import generate_insider_watch
from fin54.reports.macro_risk import generate_macro_risk_report
from fin54.reports.morning_brief import generate_morning_brief
from fin54.reports.ticker_report import generate_ticker_report
from fin54.reports.whale_proxy import generate_whale_proxy_report

SERVER_INSTRUCTIONS = """
FIN54 is the public-data financial intelligence district for Agentropolis.
Use its tools for research, monitoring, and briefing workflows. Treat FINRA OTC
outputs as aggregated public proxies, not real-time dark-pool order flow. FIN54
provides research support only and does not provide investment advice.
""".strip()

mcp = FastMCP(
    "FIN54",
    instructions=SERVER_INSTRUCTIONS,
    json_response=True,
)


def _dump(value: Any) -> Any:
    """Convert Pydantic models and nested model lists into JSON-safe values."""
    if hasattr(value, "model_dump"):
        return value.model_dump()
    if isinstance(value, list):
        return [_dump(item) for item in value]
    if isinstance(value, tuple):
        return [_dump(item) for item in value]
    if isinstance(value, dict):
        return {key: _dump(item) for key, item in value.items()}
    return value


@mcp.tool()
async def sec_company_search(name: str) -> Any:
    """Search SEC company records by company name and return matching CIK data."""
    return _dump(await sec_edgar.search_company(name))


@mcp.tool()
async def sec_recent_filings(cik: str, form_types: str | None = None) -> list[dict[str, Any]]:
    """Return recent SEC filings for a CIK, optionally filtered by comma-separated forms."""
    submissions = await sec_edgar.get_company_submissions(cik)
    forms = [item.strip() for item in form_types.split(",")] if form_types else None
    return _dump(sec_edgar.parse_filings(submissions, forms))


@mcp.tool()
async def sec_insider_activity(cik: str) -> list[dict[str, Any]]:
    """Return the FIN54 insider-activity baseline derived from SEC submissions."""
    submissions = await sec_edgar.get_company_submissions(cik)
    return _dump(sec_edgar.parse_insider_transactions(submissions))


@mcp.tool()
def market_snapshot(ticker: str, benchmark: str = "SPY") -> dict[str, Any]:
    """Return quote, technical indicators, volatility, and benchmark comparison."""
    return {
        "ticker": ticker.upper(),
        "quote": _dump(market_data.get_quote(ticker)),
        "moving_averages": _dump(market_data.get_moving_averages(ticker)),
        "rsi": _dump(market_data.get_rsi(ticker)),
        "macd": _dump(market_data.get_macd(ticker)),
        "volatility": _dump(market_data.get_volatility(ticker)),
        "benchmark_comparison": _dump(
            market_data.get_benchmark_comparison(ticker, benchmark=benchmark)
        ),
    }


@mcp.tool()
async def fred_macro_series(series_id: str) -> dict[str, Any]:
    """Retrieve a FRED macroeconomic time series by series identifier."""
    return _dump(await fred_macro.get_series(series_id))


@mcp.tool()
async def finra_otc_leaders(limit: int = 10) -> list[dict[str, Any]]:
    """Return top public FINRA OTC weekly-volume aggregates as a whale-activity proxy."""
    return _dump(await finra_otc.get_top_otc_volume(n=limit))


@mcp.tool()
def ticker_news(ticker: str, max_items: int = 20) -> list[dict[str, Any]]:
    """Return recent ticker news with FIN54's lightweight sentiment labels."""
    return _dump(news_sentiment.fetch_ticker_news(ticker, max_items=max_items))


@mcp.tool()
async def ticker_intelligence_report(ticker: str) -> dict[str, Any]:
    """Generate a synthesized ticker intelligence report from FIN54 public sources."""
    return _dump(await generate_ticker_report(ticker))


@mcp.tool()
async def morning_market_brief() -> dict[str, Any]:
    """Generate FIN54's cross-source morning market briefing."""
    return _dump(await generate_morning_brief())


@mcp.tool()
async def insider_watch_report(cik: str) -> dict[str, Any]:
    """Generate a focused insider-watch report for an SEC CIK."""
    return _dump(await generate_insider_watch(cik))


@mcp.tool()
async def macro_risk_report() -> dict[str, Any]:
    """Generate a public-data macro risk snapshot."""
    return _dump(await generate_macro_risk_report())


@mcp.tool()
async def whale_proxy_report(ticker: str) -> dict[str, Any]:
    """Generate a transparent whale-activity proxy report; not real-time order flow."""
    return _dump(await generate_whale_proxy_report(ticker))


@mcp.resource("fin54://capabilities")
def capabilities_resource() -> str:
    """Describe FIN54's available domains, boundaries, and operating role."""
    return json.dumps(
        {
            "district": "FIN54",
            "layer_role": "public-data financial reconnaissance",
            "domains": ["SEC", "FRED", "market data", "FINRA OTC", "news", "reports"],
            "transport": "stdio",
            "read_only": True,
            "limitations": [
                "not investment advice",
                "not real-time options flow",
                "not real-time dark-pool data",
                "not a trade-execution service",
            ],
        },
        indent=2,
    )


@mcp.prompt()
def analyze_ticker(ticker: str, objective: str = "risk and opportunity assessment") -> str:
    """Create a grounded workflow prompt for a FIN54 ticker investigation."""
    return (
        f"Analyze {ticker.upper()} for {objective}. Use ticker_intelligence_report, "
        "market_snapshot, ticker_news, and relevant SEC tools. Separate observed facts "
        "from inference, name data limitations, and do not present the result as investment advice."
    )


def main() -> None:
    """Run FIN54 using the standard local stdio MCP transport."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
