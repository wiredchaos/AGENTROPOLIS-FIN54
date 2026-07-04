from __future__ import annotations

import logging
from typing import Any

import httpx

from fin54.data.models import InsiderTransaction, SecFiling

logger = logging.getLogger(__name__)

BASE_URL = "https://data.sec.gov"
SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
HEADERS = {"User-Agent": "AGENTROPOLIS-FIN54 research@agentropolis.io"}


def _normalize_cik(cik: str) -> str:
    digits = "".join(ch for ch in str(cik) if ch.isdigit())
    return digits.zfill(10)


async def get_company_submissions(cik: str) -> dict:
    url = f"{BASE_URL}/submissions/CIK{_normalize_cik(cik)}.json"
    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_company_facts(cik: str) -> dict:
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{_normalize_cik(cik)}.json"
    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def get_company_concept(cik: str, taxonomy: str, concept: str) -> dict:
    url = f"{BASE_URL}/api/xbrl/companyconcept/CIK{_normalize_cik(cik)}/{taxonomy}/{concept}.json"
    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return response.json()


async def search_company(name: str) -> list[dict]:
    params = {
        "q": name,
        "dateRange": "custom",
        "startdt": "2020-01-01",
        "forms": "10-K",
    }
    async with httpx.AsyncClient(headers=HEADERS, timeout=30.0) as client:
        response = await client.get(SEARCH_URL, params=params)
        response.raise_for_status()
        payload = response.json()
    hits = payload.get("hits", {}).get("hits", payload.get("hits", []))
    results = []
    for hit in hits:
        source = hit.get("_source", hit)
        results.append(
            {
                "cik": str(source.get("cik", source.get("ciks", [""])[0])),
                "name": source.get("entityName", source.get("display_names", [""])[0]),
                "ticker": source.get("tickers", [""])[0] if isinstance(source.get("tickers"), list) else source.get("ticker", ""),
            }
        )
    return [item for item in results if item.get("name") or item.get("cik")]



def parse_filings(submissions: dict, form_types: list[str] | None = None) -> list[SecFiling]:
    recent = submissions.get("filings", {}).get("recent", {})
    if not recent:
        return []
    normalized_filter = {form.upper() for form in form_types} if form_types else None
    cik = str(submissions.get("cik", ""))
    company_name = submissions.get("name", "")
    filings: list[SecFiling] = []
    forms = recent.get("form", [])
    for idx, form in enumerate(forms):
        if normalized_filter and str(form).upper() not in normalized_filter:
            continue
        accession = str(recent.get("accessionNumber", [""])[idx]).replace("-", "")
        primary_document = recent.get("primaryDocument", [""])[idx]
        filing_cik = str(recent.get("cik", [cik] * len(forms))[idx] if isinstance(recent.get("cik"), list) else cik).lstrip("0")
        url = (
            f"https://www.sec.gov/Archives/edgar/data/{filing_cik}/{accession}/{primary_document}"
            if filing_cik and accession and primary_document
            else ""
        )
        filings.append(
            SecFiling(
                cik=cik,
                company_name=company_name,
                form_type=str(form),
                filed_date=str(recent.get("filingDate", [""])[idx]),
                period=str(recent.get("reportDate", [""])[idx]),
                url=url,
                description=str(recent.get("primaryDocDescription", [""])[idx]),
            )
        )
    return filings



def parse_insider_transactions(submissions: dict) -> list[InsiderTransaction]:
    recent = submissions.get("filings", {}).get("recent", {})
    if not recent:
        return []
    forms = recent.get("form", [])
    transactions: list[InsiderTransaction] = []
    issuer = submissions.get("name", "")
    for idx, form in enumerate(forms):
        if str(form).upper() != "4":
            continue
        accession = str(recent.get("accessionNumber", [""])[idx]).replace("-", "")
        primary_document = recent.get("primaryDocument", [""])[idx]
        cik = str(submissions.get("cik", "")).lstrip("0")
        form_url = (
            f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/{primary_document}"
            if cik and accession and primary_document
            else ""
        )
        insider_name = ""
        for key in ("insiderName", "ownerName", "reportingOwnerName"):
            values = recent.get(key)
            if isinstance(values, list) and idx < len(values):
                insider_name = str(values[idx])
                break
        title = ""
        for key in ("insiderTitle", "officerTitle", "title"):
            values = recent.get(key)
            if isinstance(values, list) and idx < len(values):
                title = str(values[idx])
                break
        tx_type = "Form 4"
        values = recent.get("transactionType")
        if isinstance(values, list) and idx < len(values):
            tx_type = str(values[idx])
        shares = 0.0
        values = recent.get("shares")
        if isinstance(values, list) and idx < len(values) and values[idx] not in (None, ""):
            shares = float(values[idx])
        price = 0.0
        values = recent.get("pricePerShare")
        if isinstance(values, list) and idx < len(values) and values[idx] not in (None, ""):
            price = float(values[idx])
        transactions.append(
            InsiderTransaction(
                issuer=issuer,
                insider_name=insider_name,
                title=title,
                transaction_type=tx_type,
                shares=shares,
                price_per_share=price,
                transaction_date=str(recent.get("filingDate", [""])[idx]),
                form_url=form_url,
            )
        )
    return transactions
