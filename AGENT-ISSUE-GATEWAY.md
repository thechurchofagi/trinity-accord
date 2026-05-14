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

## Production recommendation

The recommended production backend is a GitHub App backend.

Do not give agents a GitHub PAT.

Do not rely on anonymous `repository_dispatch`; GitHub write operations and workflow triggers require authentication.

A GitHub App backend receives the agent payload, validates it, applies rate limits, generates a short-lived GitHub App installation token server-side, and creates an intake Issue.

```text
Agent without GitHub access
  ↓ POST JSON
Agent Issue Gateway backend
  ↓ validate / rate-limit / reject secrets
GitHub App installation token
  ↓ GitHub Issues API
Issue labeled agent-gateway-intake + needs-triage
  ↓ existing triage / validation / human review
```

## Runtime options

The backend may run on:

- Node/Express (recommended)
- Vercel Function
- Netlify Function
- self-hosted server

Note: The Cloudflare Worker example has been archived (`archive/cloudflare-worker-deprecated-2026-05-14/`). It is not recommended for production.

The runtime is not the trust model. The trust model is the GitHub App with minimal repository permissions.

## Required GitHub App permissions

Repository permissions:

- Metadata: Read
- Issues: Read and write

No Contents write permission is required for the intake gateway.
No Actions write permission is required for the intake gateway.
No Administration permission is required.

## Important GitHub constraint

GitHub does not support anonymous Issue creation or anonymous `repository_dispatch` that writes to a repository. Any write operation must be performed by an authenticated user, token, OAuth app, or GitHub App.

Therefore, a public Agent Issue Gateway needs a backend. The backend must keep credentials server-side.

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
