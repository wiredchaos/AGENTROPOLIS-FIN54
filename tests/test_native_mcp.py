from __future__ import annotations

import json

import pytest

from fin54.mcp.native_server import (
    analyze_ticker,
    capabilities_resource,
    mcp,
)


@pytest.mark.asyncio
async def test_native_mcp_registers_core_tools() -> None:
    tools = await mcp.list_tools()
    names = {tool.name for tool in tools}

    assert {
        "sec_company_search",
        "sec_recent_filings",
        "sec_insider_activity",
        "market_snapshot",
        "fred_macro_series",
        "finra_otc_leaders",
        "ticker_news",
        "ticker_intelligence_report",
        "morning_market_brief",
        "insider_watch_report",
        "macro_risk_report",
        "whale_proxy_report",
    }.issubset(names)


def test_capabilities_resource_declares_safety_boundaries() -> None:
    payload = json.loads(capabilities_resource())

    assert payload["district"] == "FIN54"
    assert payload["read_only"] is True
    assert "not a trade-execution service" in payload["limitations"]


def test_ticker_prompt_requires_fact_inference_separation() -> None:
    prompt = analyze_ticker("nvda")

    assert "NVDA" in prompt
    assert "Separate observed facts from inference" in prompt
    assert "not present the result as investment advice" in prompt
