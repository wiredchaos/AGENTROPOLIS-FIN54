# FIN54 Architecture

## System overview

```text
                 +---------------------------+
                 |      External Sources     |
                 | SEC | FRED | Yahoo | RSS |
                 | FINRA | Alpha Vantage     |
                 +-------------+-------------+
                               |
                               v
+----------------+    +----------------------+    +-------------------+
| FastAPI MCP    | -> | Data adapters        | -> | Pydantic models   |
| HTTP endpoints |    | sec/fred/news/etc.   |    | typed payloads    |
+--------+-------+    +-----------+----------+    +---------+---------+
         |                            |                       |
         v                            v                       v
+--------+----------------------------+-----------------------+------+
| Report generators (ticker, macro, morning, insider, whale proxy)  |
+----------------------------+---------------------------------------+
                             |
                             v
                    +--------+---------+
                    | DuckDB cache     |
                    | local persistence|
                    +------------------+
```

## Module descriptions

- `fin54.mcp.sec_edgar`: asynchronous SEC EDGAR client for submissions, facts, concepts, and company search.
- `fin54.mcp.fred_macro`: asynchronous FRED macro client with pre-mapped economic series.
- `fin54.mcp.market_data`: synchronous market adapter built on `yfinance` with technical calculations.
- `fin54.mcp.finra_otc`: asynchronous FINRA weekly OTC volume proxy with explicit dark-pool disclaimer.
- `fin54.mcp.news_sentiment`: RSS ingestion plus deterministic keyword sentiment classification.
- `fin54.reports.*`: report synthesis layer that converts raw data into markdown-oriented sections.
- `fin54.agents.report_agent`: convenience orchestration class for downstream agent flows.
- `fin54.data.cache`: local DuckDB-first cache with sqlite in-memory fallback if DuckDB is unavailable.

## Data flow

1. A user or orchestrator calls a FastAPI endpoint.
2. The endpoint delegates to one or more MCP adapter modules.
3. Adapters normalize remote payloads into Pydantic models or structured dictionaries.
4. Report generators combine market, macro, filing, and news signals into sectioned outputs.
5. Results can optionally be persisted to DuckDB for local recall, reuse, or auditability.

## Caching strategy

FIN54 uses a local DuckDB database by default at `.cache/fin54.duckdb`. The cache abstraction ensures parent directories exist, supports generic row storage, and offers a simple SQL query interface. If DuckDB is missing in a constrained runtime, the cache automatically falls back to an in-memory sqlite database so the application can continue operating without crashing.

A practical production pattern is to cache expensive or rate-limited payloads such as FRED observations, SEC submission snapshots, or synthesized report sections keyed by ticker, series, or CIK plus retrieval date.

## MCP compatibility

The project exposes all intelligence modules through HTTP endpoints that are easy to wrap inside a Model Context Protocol transport. Each route returns JSON-friendly dictionaries and lists, while the internal report layer preserves richer semantic structure via typed Pydantic models. This separation makes FIN54 suitable as either a standalone service or an Agentropolis MCP-compatible building block.

## Adding paid providers

Paid providers should be added as parallel adapters rather than replacing the current open-data layer. A clean pattern is:

1. Create a new module under `fin54.mcp` for the provider.
2. Normalize provider-specific payloads into the existing data models wherever possible.
3. Wire provider preference or fallback order through environment configuration.
4. Keep report generators source-agnostic so premium and free inputs can be swapped without rewriting report logic.

Alpha Vantage is already scaffolded as an optional fallback quote provider. The same approach can be extended to Polygon, Intrinio, FactSet, RavenPack, or premium news/transcript feeds while keeping FIN54's public-data baseline intact.
