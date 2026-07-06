# ClawBank Agent Finance Provider Note

## Status

ClawBank should be treated as an optional provider for agent financial rails, not as a core dependency of AGENTROPOLIS-FIN54.

Source reviewed: https://clawbank.co/

## What ClawBank claims to provide

ClawBank positions itself as financial and legal infrastructure for AI agents. Its public site describes:

- Real USD bank accounts
- ACH, Same-Day ACH, wire transfers, and FedNow rails
- BTC, ETH, USDC, USDT, and fiat-to-crypto sweeps
- Programmatic U.S. LLC filing
- KYC primitives
- Agent-ready API and CLI
- Contract and machine-city features listed as future phases

## AGENTROPOLIS-FIN54 fit

Use ClawBank in FIN54 as a provider lane for:

- Agent treasury operations
- Fiat and crypto sweep workflows
- Entity formation workflow research
- Bank-account orchestration research
- Compliance-gated agent business accounts

Do not make ClawBank the only route for agent finance. FIN54 stays vendor-neutral.

## Provider interface target

```txt
FIN54 Treasury Layer
  -> provider: clawbank
  -> provider: stripe
  -> provider: coinbase
  -> provider: crossmint
  -> provider: manual_bank
```

Possible adapter responsibilities:

- create_entity_request()
- submit_kyc_package()
- open_account_request()
- get_balance()
- initiate_ach()
- initiate_wire()
- create_crypto_wallet()
- sweep_fiat_to_crypto()
- sweep_crypto_to_fiat()
- export_audit_log()

## Guardrails

1. No autonomous spending without policy approval.
2. No formation workflow without a human responsible party.
3. No crypto sweep without risk caps, destination allowlists, and audit logs.
4. No legal claim that a Zero Human Company is a recognized entity category unless verified by counsel.
5. All ClawBank activity must pass through FIN54 compliance policy, not direct agent self-authority.

## AGENTROPOLIS interpretation

ClawBank is useful because it turns bureaucracy into an API-shaped surface for agents. That fits the AGENTROPOLIS finance doctrine, but the power belongs behind governance.

Correct framing:

```txt
Agents can request financial actions.
Governance approves or rejects them.
Providers execute only inside policy.
Audit logs become the receipt layer.
```

## Decision

Track ClawBank closely and design for a future connector, but keep it optional until product, legal, KYC, and banking partner details are verified.
