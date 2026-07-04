from __future__ import annotations

from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class BaseFinModel(BaseModel):
    model_config = ConfigDict(extra="ignore")


class OHLCVBar(BaseFinModel):
    ticker: str
    date: date | datetime | str
    open: float
    high: float
    low: float
    close: float
    volume: float


class MacroSeries(BaseFinModel):
    series_id: str
    title: str
    units: str
    frequency: str
    observations: list[dict] = Field(default_factory=list)


class SecFiling(BaseFinModel):
    cik: str
    company_name: str
    form_type: str
    filed_date: str
    period: str
    url: str
    description: str


class InsiderTransaction(BaseFinModel):
    issuer: str
    insider_name: str
    title: str
    transaction_type: str
    shares: float
    price_per_share: float
    transaction_date: str
    form_url: str


class NewsItem(BaseFinModel):
    title: str
    source: str
    url: str
    published: str
    summary: str
    sentiment: Literal["bullish", "bearish", "neutral", "uncertain"]


class FinraOtcRecord(BaseFinModel):
    ticker: str
    date: str
    otc_volume: float
    tier: str
    clearing_firm: str


class TickerReport(BaseFinModel):
    ticker: str
    generated_at: datetime
    sections: dict[str, str]


class MorningBrief(BaseFinModel):
    date: date
    generated_at: datetime
    sections: dict[str, str]


class InsiderWatchReport(BaseFinModel):
    date: date
    generated_at: datetime
    transactions: list[InsiderTransaction] = Field(default_factory=list)
    summary: str


class MacroRiskReport(BaseFinModel):
    date: date
    generated_at: datetime
    sections: dict[str, str]


class WhaleProxyReport(BaseFinModel):
    date: date
    generated_at: datetime
    sections: dict[str, str]
