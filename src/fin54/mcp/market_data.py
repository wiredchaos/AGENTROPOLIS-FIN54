from __future__ import annotations

import logging
from math import sqrt

import numpy as np
import pandas as pd
import requests
import yfinance as yf

from fin54.data.models import OHLCVBar
from fin54.utils.config import ALPHA_VANTAGE_KEY

logger = logging.getLogger(__name__)


def _history(ticker: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    return yf.Ticker(ticker).history(period=period, interval=interval, auto_adjust=False)



def get_ohlcv(ticker: str, period: str = "1y", interval: str = "1d") -> list[OHLCVBar]:
    hist = _history(ticker, period=period, interval=interval)
    if hist.empty:
        return []
    bars = []
    for idx, row in hist.iterrows():
        bar_date = idx.date().isoformat() if hasattr(idx, "date") else str(idx)
        bars.append(
            OHLCVBar(
                ticker=ticker.upper(),
                date=bar_date,
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row.get("Volume", 0.0)),
            )
        )
    return bars



def get_quote(ticker: str) -> dict:
    info = dict(getattr(yf.Ticker(ticker), "fast_info", {}) or {})
    price = float(info.get("lastPrice") or info.get("regularMarketPrice") or 0.0)
    prev_close = float(info.get("previousClose") or info.get("regularMarketPreviousClose") or 0.0)
    change = price - prev_close if prev_close else 0.0
    change_pct = (change / prev_close * 100.0) if prev_close else 0.0
    return {
        "ticker": ticker.upper(),
        "price": price,
        "change": change,
        "change_pct": change_pct,
        "volume": float(info.get("lastVolume") or info.get("regularMarketVolume") or 0.0),
    }



def get_moving_averages(ticker: str, periods: list[int] | None = None) -> dict:
    if periods is None:
        periods = [20, 50, 200]
    hist = _history(ticker, period="1y", interval="1d")
    close = hist["Close"] if not hist.empty else pd.Series(dtype=float)
    return {f"sma_{period}": float(close.rolling(period).mean().iloc[-1]) for period in periods if len(close) >= period}



def get_rsi(ticker: str, period: int = 14) -> float:
    hist = _history(ticker, period="1y", interval="1d")
    if hist.empty or len(hist) <= period:
        return float("nan")
    close = hist["Close"]
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    return float(rsi.iloc[-1])



def get_macd(ticker: str) -> dict:
    hist = _history(ticker, period="1y", interval="1d")
    if hist.empty:
        return {"macd": 0.0, "signal": 0.0, "histogram": 0.0}
    close = hist["Close"]
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line
    return {
        "macd": float(macd_line.iloc[-1]),
        "signal": float(signal_line.iloc[-1]),
        "histogram": float(histogram.iloc[-1]),
    }



def get_volatility(ticker: str, window: int = 30) -> float:
    hist = _history(ticker, period="1y", interval="1d")
    if hist.empty or len(hist) <= window:
        return float("nan")
    returns = np.log(hist["Close"] / hist["Close"].shift(1))
    vol = returns.rolling(window).std() * sqrt(252)
    return float(vol.iloc[-1])



def get_benchmark_comparison(ticker: str, benchmark: str = "SPY", period: str = "1y") -> dict:
    stock = _history(ticker, period=period, interval="1d")
    bench = _history(benchmark, period=period, interval="1d")
    if stock.empty or bench.empty:
        return {"ticker": ticker.upper(), "benchmark": benchmark.upper(), "correlation": 0.0, "beta": 0.0, "alpha": 0.0}
    joined = pd.concat([stock["Close"].pct_change(), bench["Close"].pct_change()], axis=1, join="inner").dropna()
    joined.columns = ["stock", "bench"]
    if joined.empty:
        return {"ticker": ticker.upper(), "benchmark": benchmark.upper(), "correlation": 0.0, "beta": 0.0, "alpha": 0.0}
    correlation = float(joined["stock"].corr(joined["bench"]))
    bench_var = float(joined["bench"].var())
    covariance = float(joined[["stock", "bench"]].cov().iloc[0, 1])
    beta = covariance / bench_var if bench_var else 0.0
    alpha = float(joined["stock"].mean() * 252 - beta * joined["bench"].mean() * 252)
    return {
        "ticker": ticker.upper(),
        "benchmark": benchmark.upper(),
        "correlation": correlation,
        "beta": beta,
        "alpha": alpha,
    }



def get_alpha_vantage_quote(ticker: str) -> dict:
    if not ALPHA_VANTAGE_KEY:
        return {}
    params = {"function": "GLOBAL_QUOTE", "symbol": ticker, "apikey": ALPHA_VANTAGE_KEY}
    response = requests.get("https://www.alphavantage.co/query", params=params, timeout=30)
    response.raise_for_status()
    quote = response.json().get("Global Quote", {})
    return {
        "ticker": ticker.upper(),
        "price": float(quote.get("05. price", 0.0) or 0.0),
        "change": float(quote.get("09. change", 0.0) or 0.0),
        "change_pct": float(str(quote.get("10. change percent", "0")).replace("%", "") or 0.0),
        "volume": float(quote.get("06. volume", 0.0) or 0.0),
    }
