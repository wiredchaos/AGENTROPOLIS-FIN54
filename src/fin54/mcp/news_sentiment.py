from __future__ import annotations

import logging
from typing import Literal

import feedparser

from fin54.data.models import NewsItem

logger = logging.getLogger(__name__)

RSS_FEEDS = [
    "https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
    "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best",
    "https://feeds.marketwatch.com/marketwatch/topstories/",
]
BULLISH_KEYWORDS = ["surge", "rally", "beat", "strong", "growth", "record", "upgrade", "positive", "gains", "outperform", "profit", "revenue growth"]
BEARISH_KEYWORDS = ["decline", "fall", "miss", "weak", "loss", "downgrade", "negative", "drop", "underperform", "risk", "warning", "cut", "deficit"]



def fetch_rss_feed(url: str) -> list[dict]:
    parsed = feedparser.parse(url)
    items = []
    default_source = parsed.feed.get("title", "RSS")
    for entry in parsed.entries:
        source = default_source
        if isinstance(entry.get("source"), dict):
            source = entry.get("source", {}).get("title", default_source)
        items.append(
            {
                "title": entry.get("title", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
                "source": source,
                "url": entry.get("link", ""),
            }
        )
    return items



def classify_sentiment(text: str) -> Literal["bullish", "bearish", "neutral", "uncertain"]:
    lower = (text or "").lower()
    bullish_count = sum(lower.count(keyword) for keyword in BULLISH_KEYWORDS)
    bearish_count = sum(lower.count(keyword) for keyword in BEARISH_KEYWORDS)
    score = bullish_count - bearish_count
    if bullish_count == 0 and bearish_count == 0:
        return "uncertain"
    if score > 0:
        return "bullish"
    if score < 0:
        return "bearish"
    return "neutral"



def fetch_ticker_news(ticker: str, max_items: int = 20) -> list[NewsItem]:
    items = fetch_rss_feed(RSS_FEEDS[0].format(ticker=ticker.upper()))
    news = []
    for item in items[:max_items]:
        text = f"{item['title']} {item['summary']}"
        news.append(
            NewsItem(
                title=item["title"],
                source=item["source"],
                url=item["url"],
                published=item["published"],
                summary=item["summary"],
                sentiment=classify_sentiment(text),
            )
        )
    return news



def fetch_market_news(max_items: int = 20) -> list[NewsItem]:
    collected: list[NewsItem] = []
    for url in RSS_FEEDS[1:]:
        try:
            items = fetch_rss_feed(url)
        except Exception as exc:
            logger.warning("RSS fetch failed for %s: %s", url, exc)
            continue
        for item in items:
            text = f"{item['title']} {item['summary']}"
            collected.append(
                NewsItem(
                    title=item["title"],
                    source=item["source"],
                    url=item["url"],
                    published=item["published"],
                    summary=item["summary"],
                    sentiment=classify_sentiment(text),
                )
            )
    return collected[:max_items]



def summarize_ticker_narrative(ticker: str, news_items: list[NewsItem]) -> str:
    if not news_items:
        return f"Recent coverage for {ticker.upper()} is sparse, so the narrative is currently inconclusive."
    counts = {label: 0 for label in ["bullish", "bearish", "neutral", "uncertain"]}
    for item in news_items:
        counts[item.sentiment] += 1
    headlines = "; ".join(item.title for item in news_items[:3])
    max_count = max(counts.values())
    dominant_candidates = [label for label, cnt in counts.items() if cnt == max_count]
    dominant = dominant_candidates[0] if len(dominant_candidates) == 1 else "mixed"
    return (
        f"{ticker.upper()} has {len(news_items)} recent tracked headlines with sentiment split of "
        f"{counts['bullish']} bullish, {counts['bearish']} bearish, {counts['neutral']} neutral, and "
        f"{counts['uncertain']} uncertain. The dominant tone is {dominant}. Key headlines include: {headlines}."
    )
