# FIN54 Market Intelligence Pack

## Purpose

Absorb the legacy February 2026 technical-analysis work into the September 2026 Agentropolis finance architecture without granting trading authority.

FIN54 owns research-grade market observation, feature extraction, transforms, pattern detection, confluence analysis, and normalized market-evidence generation. It does not authorize trades, custody assets, move funds, or bypass ATG, AEGIS, Fiscal Command, Pay Protocol, or PAYRAIL boundaries.

## Capability Families

### Features
- ATR
- RSI
- MACD
- stochastic oscillators
- momentum
- volume / OBV
- moving averages
- volatility

### Transforms
- Heikin Ashi
- Renko

### Structure Detectors
- Fibonacci retracement / extension
- support and resistance
- dynamic support and resistance
- trendlines
- fair value gaps
- breakout
- reversal

### Pattern Models
- candlestick patterns
- harmonic patterns
- Elliott Wave
- Gann-angle models

### Experimental / Quarantined
- lunar-cycle / moon-phase correlation
- subjective wave labeling without confidence and invalidation metadata
- any detector without reproducible backtest fixtures

Experimental capabilities MUST NOT increase execution authority.

## Output Contract

Pattern modules emit `MarketEvidence`, not BUY/SELL commands.

Minimum fields:

```json
{
  "version": "1.0.0",
  "instrument": "ETH-USDC",
  "timeframe": "4h",
  "observation": {
    "type": "breakout",
    "direction": "bullish"
  },
  "evidence": {},
  "confidence": 0.0,
  "invalidations": [],
  "provenance": {
    "detector": "market.breakout.detect",
    "detector_version": "1.0.0",
    "source_hash": ""
  },
  "authority": {
    "trade_authority": "none"
  }
}
```

## Layering

```text
market data
  -> transforms
  -> features
  -> detectors
  -> structure models
  -> regime / confluence
  -> MarketEvidence
  -> ontology / thesis agents
  -> ATG semantic object
  -> risk compilation
  -> Execution Envelope
  -> AEGIS / fiscal gates
  -> approved execution adapter
  -> receipt / audit
```

## Correlation Guardrail

Confluence MUST NOT count correlated indicators as independent votes. RSI, MACD, moving averages, momentum, and related derivatives require feature-family grouping or correlation-aware weighting.

## Rust Boundary

Keep research, ingestion, exploratory analytics, detector orchestration, and reports Python-first.

Move or implement in Rust when used for consequential automated finance:
- deterministic portfolio / risk kernels
- signed market-evidence hashing
- canonical serialization
- execution / pre-trade risk gates
- replay and idempotency protection
- settlement / signing integration

## Authority

FIN54 observes and explains. It does not grant spending, custody, treasury, or trading authority.
