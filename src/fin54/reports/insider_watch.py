from __future__ import annotations

import logging
from datetime import UTC, date, datetime

from fin54.data.models import InsiderWatchReport
from fin54.mcp import sec_edgar

logger = logging.getLogger(__name__)


async def generate_insider_watch(cik: str) -> InsiderWatchReport:
    transactions = []
    summary = "No insider transactions were identified."
    try:
        submissions = await sec_edgar.get_company_submissions(cik)
        transactions = sec_edgar.parse_insider_transactions(submissions)
        company_name = submissions.get("name", cik)
        if transactions:
            summary = (
                f"Detected {len(transactions)} recent Form 4 filing(s) for {company_name}. "
                f"Most recent filer: {transactions[0].insider_name or 'undisclosed insider'} on {transactions[0].transaction_date}."
            )
        else:
            summary = f"No recent Form 4 transactions were identified for {company_name}."
    except Exception as exc:
        logger.warning("insider watch generation failed for %s: %s", cik, exc)
        summary = f"Insider watch data for CIK {cik} is temporarily unavailable."
    return InsiderWatchReport(date=date.today(), generated_at=datetime.now(UTC), transactions=transactions, summary=summary)
