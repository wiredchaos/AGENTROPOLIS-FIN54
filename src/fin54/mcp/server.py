from __future__ import annotations

import logging

import uvicorn
from fastapi import FastAPI, HTTPException, Query

from fin54.mcp import finra_otc, fred_macro, market_data, news_sentiment, sec_edgar
from fin54.reports.insider_watch import generate_insider_watch
from fin54.reports.macro_risk import generate_macro_risk_report
from fin54.reports.morning_brief import generate_morning_brief
from fin54.reports.ticker_report import generate_ticker_report
from fin54.reports.whale_proxy import generate_whale_proxy_report

logger = logging.getLogger(__name__)

app = FastAPI(title="FIN54 Financial Intelligence MCP", version="0.1.0")


@app.get("/sec/submissions/{cik}")
async def sec_submissions(cik: str):
    try:
        return await sec_edgar.get_company_submissions(cik)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/sec/facts/{cik}")
async def sec_facts(cik: str):
    try:
        return await sec_edgar.get_company_facts(cik)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/sec/filings/{cik}")
async def sec_filings(cik: str, form_types: str | None = Query(default=None)):
    try:
        submissions = await sec_edgar.get_company_submissions(cik)
        forms = [item.strip() for item in form_types.split(",")] if form_types else None
        return [item.model_dump() for item in sec_edgar.parse_filings(submissions, forms)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/sec/insider/{cik}")
async def sec_insider(cik: str):
    try:
        submissions = await sec_edgar.get_company_submissions(cik)
        return [item.model_dump() for item in sec_edgar.parse_insider_transactions(submissions)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/sec/search")
async def sec_search(name: str = Query(...)):
    try:
        return await sec_edgar.search_company(name)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/fred/series/{series_id}")
async def fred_series(series_id: str):
    try:
        return (await fred_macro.get_series(series_id)).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/fred/series")
async def fred_series_list():
    return fred_macro.SERIES


@app.get("/market/ohlcv/{ticker}")
def market_ohlcv(ticker: str, period: str = "1y", interval: str = "1d"):
    try:
        return [item.model_dump() for item in market_data.get_ohlcv(ticker, period=period, interval=interval)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/market/quote/{ticker}")
def market_quote(ticker: str):
    try:
        return market_data.get_quote(ticker)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/market/technicals/{ticker}")
def market_technicals(ticker: str):
    try:
        return {
            "moving_averages": market_data.get_moving_averages(ticker),
            "rsi": market_data.get_rsi(ticker),
            "macd": market_data.get_macd(ticker),
            "volatility": market_data.get_volatility(ticker),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/market/comparison/{ticker}")
def market_comparison(ticker: str, benchmark: str = "SPY"):
    try:
        return market_data.get_benchmark_comparison(ticker, benchmark=benchmark)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/finra/otc/summary")
async def finra_summary(limit: int = 20):
    try:
        return [item.model_dump() for item in await finra_otc.get_otc_weekly_summary(limit=limit)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/finra/otc/top")
async def finra_top(n: int = 10):
    try:
        return [item.model_dump() for item in await finra_otc.get_top_otc_volume(n=n)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/news/ticker/{ticker}")
def news_ticker(ticker: str, max_items: int = 20):
    try:
        return [item.model_dump() for item in news_sentiment.fetch_ticker_news(ticker, max_items=max_items)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/news/market")
def news_market(max_items: int = 20):
    try:
        return [item.model_dump() for item in news_sentiment.fetch_market_news(max_items=max_items)]
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/report/ticker/{ticker}")
async def report_ticker(ticker: str):
    try:
        return (await generate_ticker_report(ticker)).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/report/morning-brief")
async def report_morning_brief():
    try:
        return (await generate_morning_brief()).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/report/insider-watch")
async def report_insider_watch(cik: str):
    try:
        return (await generate_insider_watch(cik)).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/report/macro-risk")
async def report_macro_risk():
    try:
        return (await generate_macro_risk_report()).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/report/whale-proxy")
async def report_whale_proxy(ticker: str):
    try:
        return (await generate_whale_proxy_report(ticker)).model_dump()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8054)
