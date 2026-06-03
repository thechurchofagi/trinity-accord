---
title: "Operator Secrets"
permalink: /docs/operator-secrets/
---

# Operator Secrets

This repository intentionally uses the following GitHub repository secret names.

Do not rename these secrets unless every workflow, script, and this document are updated together.

## Required repository secrets

| Secret | Meaning | Used by |
|---|---|---|
| `ARKEY` | Arweave wallet key. May be raw JWK JSON or base64-encoded JWK JSON. | Arweave archive uploader and smoke checks |
| `ETH_RPC` | Ethereum JSON-RPC endpoint. Not required for Arweave upload. Reserved for chain/RPC smoke checks and future mirror anchoring. | Operator secret smoke checks |
| `GH_PAT` | GitHub Personal Access Token for explicit repository API operations when built-in `GITHUB_TOKEN` is not enough. | Optional external/runtime maintenance scripts |
| `RENDER` | Render API key. | Explicit manual Render deployment workflow |

## Rules

- Do not print secret values.
- Do not commit secret values.
- Do not write secret values into public JSON.
- Do not write secret values into archive manifests.
- Prefer GitHub Actions built-in `GITHUB_TOKEN` for in-repository automation.
- Use `GH_PAT` only for external runtimes or explicit maintenance scripts.
- Use `RENDER` only in manual deployment workflows.
- Use `ARKEY` only in Arweave smoke/upload steps.
- `ETH_RPC` is not required for Arweave upload.
