from fin54.mcp.sec_edgar import parse_filings, parse_insider_transactions


MOCK_SUBMISSIONS = {
    "cik": "0000123456",
    "name": "Example Corp",
    "filings": {
        "recent": {
            "form": ["10-K", "10-Q", "4"],
            "filingDate": ["2024-02-01", "2024-05-01", "2024-05-10"],
            "reportDate": ["2023-12-31", "2024-03-31", "2024-05-09"],
            "accessionNumber": ["0000123456-24-000001", "0000123456-24-000002", "0000123456-24-000003"],
            "primaryDocument": ["annual.htm", "quarterly.htm", "form4.htm"],
            "primaryDocDescription": ["Annual report", "Quarterly report", "Statement of changes"],
            "insiderName": ["", "", "Jane Doe"],
            "insiderTitle": ["", "", "CEO"],
            "transactionType": ["", "", "Purchase"],
            "shares": ["", "", 15000],
            "pricePerShare": ["", "", 12.5],
        }
    },
}


def test_parse_filings_filters_and_builds_urls():
    filings = parse_filings(MOCK_SUBMISSIONS, ["10-K", "4"])
    assert len(filings) == 2
    assert filings[0].form_type == "10-K"
    assert filings[0].company_name == "Example Corp"
    assert filings[0].url.endswith("annual.htm")
    assert filings[1].form_type == "4"


def test_parse_insider_transactions_extracts_form4_metadata():
    transactions = parse_insider_transactions(MOCK_SUBMISSIONS)
    assert len(transactions) == 1
    tx = transactions[0]
    assert tx.issuer == "Example Corp"
    assert tx.insider_name == "Jane Doe"
    assert tx.transaction_type == "Purchase"
    assert tx.shares == 15000
    assert tx.price_per_share == 12.5
