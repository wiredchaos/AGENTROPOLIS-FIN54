from fin54.data.models import NewsItem
from fin54.mcp.news_sentiment import classify_sentiment, summarize_ticker_narrative


def test_classify_sentiment_variants():
    assert classify_sentiment("A strong rally with record profit") == "bullish"
    assert classify_sentiment("A weak decline with downgrade risk") == "bearish"
    assert classify_sentiment("Positive upgrade offsets negative warning") == "neutral"
    assert classify_sentiment("Board schedules annual meeting") == "uncertain"


def test_summarize_ticker_narrative_structure():
    items = [
        NewsItem(title="ACME posts strong growth", source="Wire", url="https://example.com/1", published="today", summary="profit surge", sentiment="bullish"),
        NewsItem(title="ACME cuts guidance", source="Wire", url="https://example.com/2", published="today", summary="warning", sentiment="bearish"),
    ]
    summary = summarize_ticker_narrative("ACME", items)
    assert "ACME" in summary
    assert "bullish" in summary
    assert "Key headlines include" in summary
