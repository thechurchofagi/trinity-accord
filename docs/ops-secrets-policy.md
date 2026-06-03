---
title: "Operations Secrets Policy"
permalink: /docs/ops-secrets-policy/
---

# Operations Secrets Policy

See also: [Operator Secrets](/docs/operator-secrets/) for canonical secret names.

## Secrets

### ARKEY

**Purpose:** Arweave archive uploader wallet key. May be raw JWK JSON or base64-encoded JWK JSON.

**Rules:**

- Do not use the main identity wallet.
- Do not use a wallet holding significant funds.
- Do not commit wallet JSON.
- Do not paste wallet JSON into issues, logs, or chat.
- Store in GitHub Actions secret `ARKEY`.
- Workflows must never echo the secret.
- Rotate wallet if exposed.
- Keep live upload disabled until dry-run archive tests pass.

### ETH_RPC

**Purpose:** Ethereum JSON-RPC endpoint for chain/RPC smoke checks and future mirror anchoring.

### GH_PAT

**Purpose:** GitHub Personal Access Token for external runtime or maintenance scripts. Prefer `GITHUB_TOKEN` for in-repo automation.

### RENDER

**Purpose:** Render API key for explicit manual deployment workflows only.

## General Policy

- Never print secrets in workflow logs.
- Never commit secrets to the repository.
- Use GitHub Actions secrets for all sensitive values.
- Rotate secrets if exposure is suspected.
