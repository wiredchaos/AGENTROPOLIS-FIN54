# FIN54

FIN54 is the open-data financial intelligence district for Agentropolis. It combines market, macro, regulatory, OTC proxy, and news signals into both a native Model Context Protocol server and an optional FastAPI gateway.

The design goal is strategic breadth over proprietary depth: give agents a dependable baseline for situational awareness, briefing generation, and cross-source synthesis without requiring expensive terminals or vendor contracts on day one.

## Open data sources used

| Source | Type | Access |
| --- | --- | --- |
| SEC EDGAR | Filings, company facts, concepts | Public API |
| FRED | Macro time series | Public API, optional key |
| Yahoo Finance | Quotes, OHLCV, benchmark data | Public package access |
| Yahoo Finance RSS | Ticker headlines | Public RSS |
| Reuters / MarketWatch RSS | Market headlines | Public RSS |
| FINRA OTC weekly summary | Aggregated OTC volume proxy | Public API |
| Alpha Vantage | Optional quote fallback | Free API key |

## What it can replicate

- Rapid ticker tear sheets with price action, technicals, and news tone
- Morning market briefings for agent planning loops
- SEC filing and Form 4 surveillance baselines
- Macro risk snapshots using public FRED indicators
- OTC activity proxy views using public FINRA aggregates

## What it cannot replicate

- Real-time dark-pool or institutional order-flow visibility
- Premium transcripts, estimates, or alternative-data products
- Tick-level execution analytics or low-latency trading signals
- Human analyst judgment on ambiguous narratives or filings

## How it fits Agentropolis

FIN54 is the public-data reconnaissance layer inside Agentropolis. It gives planning, research, and monitoring agents a consistent read-only interface for external financial context. It is not a trade-execution service and does not provide investment advice.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

On Windows PowerShell, activate the environment with:

```powershell
.\.venv\Scripts\Activate.ps1
```

## Run the native MCP server

FIN54 now includes a native stdio MCP server:

```bash
fin54-mcp
```

Equivalent module command:

```bash
python -m fin54.mcp.native_server
```

Example MCP client configuration:

```json
{
  "mcpServers": {
    "fin54": {
      "command": "fin54-mcp"
    }
  }
}
```

### Native MCP contracts

The server registers read-only tools for:

- SEC company search, recent filings, and insider activity
- Market snapshots with quote, technicals, volatility, and benchmark comparison
- FRED macro series
- FINRA OTC public-volume leaders
- Ticker news and lightweight sentiment
- Ticker intelligence, morning brief, insider watch, macro risk, and whale-proxy reports

It also exposes:

- Resource: `fin54://capabilities`
- Prompt: `analyze_ticker`

## Run the optional REST gateway

```bash
python -m fin54.mcp.server
```

The REST service starts on `http://0.0.0.0:8054`.

## Test

```bash
pytest -q
```

## Adding paid providers

Alpha Vantage is wired as an optional quote fallback through `ALPHA_VANTAGE_KEY`. To extend FIN54, add a provider adapter under `src/fin54/mcp`, normalize outputs into the existing Pydantic models, and keep report generators source-agnostic so premium sources can be added without changing downstream Agentropolis consumers.

## License and disclaimer

FIN54 is provided under the repository license. It is for research and agentic workflow support only, not investment advice. FINRA OTC outputs are aggregated public summaries and explicitly not real-time dark-pool data.
