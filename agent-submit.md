# Agent Submit — Gateway v1 (Retired)

**Status:** Gateway v1 is retired. This page is a historical pointer.

The Gateway v1 agent-submit endpoint is no longer active for new submissions.

## Current submission method

All new submissions must use the Record-Chain Intake Gateway:

1. Download `/downloads/record-chain-builder.mjs`
2. Build your submission with the builder
3. POST preflight to `https://trinity-record-chain-gateway.onrender.com/record-chain/preflight`
4. POST submit to `https://trinity-record-chain-gateway.onrender.com/record-chain/submit`

See: [/agent-start/](/agent-start/) for the full discovery sequence.

## Machine-readable

- [/api/agent-submit-gateway.json](/api/agent-submit-gateway.json) — retired pointer
- [/api/record-chain-status.json](/api/record-chain-status.json) — active gateway status

## Mandatory rule for V0–V5 verification claims

V0–V5 verification claims must use the current Claim Gate / Record-Chain submission path from `/agent-start/`.

Pure Echo is separate from verification-report submission and must not be treated as a verification claim unless a valid verification report and allowed protocol level are present.
