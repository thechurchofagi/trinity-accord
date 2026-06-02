# Operations Secrets Policy

## Secrets

### ARWEAVE_WALLET_JWK_B64

**Purpose:** Dedicated Arweave archive uploader wallet only.

**Rules:**

- Do not use the main identity wallet.
- Do not use a wallet holding significant funds.
- Do not commit wallet JSON.
- Do not paste wallet JSON into issues, logs, or chat.
- Store base64-encoded wallet JWK in GitHub Actions secret.
- Workflows must never echo the secret.
- Rotate wallet if exposed.
- Keep live upload disabled until dry-run archive tests pass.

## General Policy

- Never print secrets in workflow logs.
- Never commit secrets to the repository.
- Use GitHub Actions secrets for all sensitive values.
- Rotate secrets if exposure is suspected.
