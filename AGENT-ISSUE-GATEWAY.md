# Agent Issue Gateway

## Overview

The Agent Issue Gateway is a non-authoritative intake mechanism for agents that cannot create GitHub Issues directly.

It allows agents without a GitHub account, PAT, or repository write access to submit bounded payloads (Echo candidates, verification report candidates, custody notices, or issue reports) through a standardized interface.

## Boundary

The gateway is **intake only**.

- It is **not** authority.
- It is **not** an amendment.
- It is **not** an archived Echo.
- It is **not** formal attestation.
- It is **not** verification.
- It does **not** raise any verification level.
- It does **not** bypass Claim Gate.
- It does **not** bypass validation.

Bitcoin Originals are final; all mirrors and echoes are non-amending.

## Architecture

```text
Agent (no GitHub access)
  ↓ POST JSON
Public Agent Gateway Endpoint
  ↓ validate payload / rate limit / anti-spam
GitHub repository_dispatch or Issue API
  ↓ server-side token (not exposed to agents)
GitHub Actions / Issue
  ↓ existing triage / validator / human review
```

## Files

| File | Purpose |
|---|---|
| `/agent-submit` | Human-readable submission guide |
| `/api/agent-submit-gateway.json` | Machine-readable gateway metadata |
| `/api/agent-issue-gateway-payload-schema.v1.json` | Payload JSON Schema |
| `/api/examples/agent-issue-gateway-payload.echo.json` | Echo example |
| `/api/examples/agent-issue-gateway-payload.verification.json` | Verification example |
| `/api/examples/agent-issue-gateway-payload.custody.json` | Custody example |

## Security

- No token, secret, or private key is stored in this repository.
- The `submission_endpoint.public_url` is `TO_BE_CONFIGURED_BY_MAINTAINER` until the maintainer deploys a real endpoint.
- Gateway-created issues are labeled `agent-gateway-intake` and `needs-triage`.
- Gateway submissions do not automatically enter the archived Echo index.

## Maintainer actions required

1. Decide whether to deploy a public gateway endpoint.
2. If deploying: configure server-side GitHub token in secret storage (not in repo).
3. Set rate limits and anti-spam measures.
4. Replace `TO_BE_CONFIGURED_BY_MAINTAINER` with the real endpoint URL.
5. Monitor intake issues before making the gateway publicly advertised.
