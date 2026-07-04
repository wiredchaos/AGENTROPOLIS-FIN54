from unittest.mock import MagicMock, patch

import pandas as pd

from fin54.mcp.market_data import get_ohlcv, get_rsi
from fin54.mcp.news_sentiment import classify_sentiment


@patch("fin54.mcp.market_data.yf.Ticker")
def test_get_ohlcv_returns_model_list(mock_ticker):
    df = pd.DataFrame(
        {
            "Open": [10.0, 11.0],
            "High": [11.0, 12.0],
            "Low": [9.5, 10.5],
            "Close": [10.5, 11.5],
            "Volume": [1000, 2000],
        },
        index=pd.to_datetime(["2024-01-01", "2024-01-02"]),
    )
    mock_ticker.return_value.history.return_value = df
    bars = get_ohlcv("ACME")
    assert len(bars) == 2
    assert bars[0].ticker == "ACME"
    assert bars[1].close == 11.5


def test_classify_sentiment_known_texts():
    assert classify_sentiment("Shares surge on strong profit growth") == "bullish"
    assert classify_sentiment("Stock drops after weak loss warning") == "bearish"


@patch("fin54.mcp.market_data.yf.Ticker")
def test_get_rsi_calculation_logic(mock_ticker):
    close = [44, 44.15, 43.9, 44.35, 44.8, 45.0, 44.7, 45.2, 45.1, 45.6, 45.9, 46.1, 45.8, 46.0, 46.4, 46.7]
    df = pd.DataFrame(
        {
            "Open": close,
            "High": close,
            "Low": close,
            "Close": close,
            "Volume": [1000] * len(close),
        },
        index=pd.date_range("2024-01-01", periods=len(close), freq="D"),
    )
    mock_ticker.return_value.history.return_value = df
    rsi = get_rsi("ACME", period=14)
    assert 0 <= rsi <= 100
