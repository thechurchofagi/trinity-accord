# Record-Chain Intake Gateway

A FastAPI microservice that validates, sanitizes, and persists record submissions into the Trinity Accord record-chain repository via the GitHub Contents API.

## Purpose

This gateway sits between agent clients and the Trinity record-chain store. It:

- **Validates** incoming submissions against JSON schemas and security rules
- **Rejects** forbidden chain fields, private keys, and placeholder tokens
- **Enforces** context-completeness minimums per record type and verification version
- **Persists** approved records as canonical JSON files in the target repo
- **Returns** signed receipts with SHA-256 content hashes

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Liveness probe |
| `GET` | `/record-chain/readiness` | Config readiness check (no secrets exposed) |
| `POST` | `/record-chain/preflight` | Validate a submission without writing |
| `POST` | `/record-chain/submit` | Validate, persist, and return receipt |
| `GET` | `/record-chain/receipt/{receipt_id}` | Retrieve a stored receipt |
| `POST` | `/gateway/preflight` | Retired — points to `/record-chain/preflight` |
| `POST` | `/agent-submit` | Retired — points to `/record-chain/submit` |

## Configuration

All configuration is via environment variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `TRINITY_REPO_FULL_NAME` | Yes | Target repo (e.g. `org/repo`) |
| `TRINITY_TARGET_BRANCH` | Yes | Branch to write to (e.g. `main`) |
| `TRINITY_GITHUB_TOKEN` | Yes | GitHub PAT with Contents write access |
| `TRINITY_GATEWAY_BASE_URL` | No | Base URL for the Trinity Gateway runtime |
| `TRINITY_GATEWAY_RUNTIME_VERSION` | No | Expected runtime version string |
| `TRINITY_MAX_SUBMISSION_BYTES` | No | Max request body size (default: 524288) |
| `TRINITY_SUBMIT_WRITE_MODE` | No | `commit` (default) or `dry-run` |

## Running locally

```bash
pip install -r requirements.txt
export TRINITY_REPO_FULL_NAME=your-org/your-repo
export TRINITY_TARGET_BRANCH=main
export TRINITY_GITHUB_TOKEN=<YOUR_PAT_HERE>  # Never paste real PATs
uvicorn app:app --reload --port 8000
```

> **Security:** Never paste real PATs into issues, logs, chat, or commits.

## Deployment

This service is configured for Render via `render.yaml`. Set the secret environment variables in the Render dashboard.
