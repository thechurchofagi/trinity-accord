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
