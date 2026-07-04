from datetime import UTC, date, datetime

from fin54.data.models import MorningBrief, TickerReport



def test_ticker_report_model_validation():
    report = TickerReport(
        ticker="ACME",
        generated_at=datetime.now(UTC),
        sections={"overview": "Test", "technicals": "Test", "news_sentiment": "Test"},
    )
    assert report.ticker == "ACME"
    assert "overview" in report.sections



def test_morning_brief_model_validation():
    brief = MorningBrief(
        date=date.today(),
        generated_at=datetime.now(UTC),
        sections={"macro_snapshot": "Macro", "market_overview": "Markets", "news_highlights": "News"},
    )
    assert brief.date == date.today()
    assert "market_overview" in brief.sections
