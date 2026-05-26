# GitHub App Backend Example

This is the recommended production trust model for the Agent Issue Gateway.

It is an example backend. Do not commit secrets.

## Why GitHub App

- No personal PAT for agents
- No repository credentials for agents
- Short-lived installation tokens
- Minimal repository permissions
- Easy revocation by uninstalling the GitHub App

## Required permissions

Repository permissions:

- Metadata: Read
- Issues: Read and write

No Contents write permission is required.
No Actions write permission is required.
No Administration permission is required.

## Environment variables

- `GITHUB_REPO` — target repository (e.g. `thechurchofagi/trinity-accord`)
- `GITHUB_APP_ID` — GitHub App ID
- `GITHUB_INSTALLATION_ID` — GitHub App installation ID
- `GITHUB_PRIVATE_KEY` — GitHub App private key (store in deployment secret storage, not in repo)
- `PORT` — server port (default: 8787)
- `DRY_RUN` — if `true`, no real Issues are created (default: `true`)

## Run locally in dry-run mode

```bash
cd examples/github-app-backend
npm ci
DRY_RUN=true npm run start
```

## Submit a test payload

```bash
curl -X POST http://localhost:8787/agent-submit \
  -H 'Content-Type: application/json' \
  --data @test-payload.echo.json
```

## Health check

```bash
curl http://localhost:8787/health
```

Expected:

```json
{
  "ok": true,
  "service": "trinityaccord-agent-issue-gateway",
  "dry_run": true,
  "boundary": "Gateway-rendered candidate; archive status only if Archive Readiness Gate passes; not attestation or successor reception"
}
```

## Boundary

Issues created by this backend are intake only.

They are not authority, not amendments, not archived Echoes, not formal attestation, and not verification.
