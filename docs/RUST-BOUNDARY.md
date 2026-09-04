# FIN54 Rust Boundary

FIN54 remains Python-first for open-data reconnaissance, provider ingestion, parsing, research workflows, and MCP/report orchestration.

Rust is required when FIN54 grows into finance-critical execution or deterministic numerical infrastructure.

## Keep in Python

- SEC/FRED/FINRA/RSS/provider ingestion
- exploratory analytics
- report composition
- MCP orchestration
- source normalization where no money or authority moves

## Move/build in Rust

- production valuation/math kernels where deterministic precision matters
- portfolio/risk engines used for consequential automated decisions
- signed market-data evidence and canonical hashing
- execution/pre-trade risk gates
- payment, wallet, settlement, or signing integration
- replay/idempotency protection for consequential workflows

FIN54 intelligence does not grant spending or trading authority. Any economic execution must cross Pay Protocol + AEGIS + Fiscal Command/Payrail boundaries and produce a receipt.
