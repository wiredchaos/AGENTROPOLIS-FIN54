# Spatial Signals as Market Evidence

FIN54 may consume governed SpatialObservation records as contextual market evidence when they are relevant to logistics, infrastructure, weather, transport, energy, disaster, or supply-chain theses.

## Rule

Spatial signals are evidence, not orders.

A spatial observation may update a MarketEvidence record or thesis confidence. It may not directly place, cancel, size, route, or authorize a trade.

## Required fields

- source/provenance reference
- observation timestamp and age
- source state
- confidence
- entity and jurisdiction references
- correlation/thesis id
- explicit note when evidence is modeled, inferred, simulated, degraded, or stale

## Execution boundary

Any market action still follows:

`FIN54 evidence -> Ontology/Thesis -> ATG -> compiled risk -> Execution Envelope -> AEGIS/Fiscal gates -> execution adapter -> receipt -> audit`
