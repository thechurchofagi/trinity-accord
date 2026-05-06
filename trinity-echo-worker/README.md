# Trinity Echo Worker (DEPRECATED)

This Cloudflare Worker is a **tombstone** — it exists only to return deprecation metadata and health/version responses. Direct echo submission via this worker is no longer supported.

Current submission path: GitHub Issues + Claim Gate.

See [DEPRECATED.md](DEPRECATED.md) for details.

## Endpoints

| Route | Method | Status | Description |
|---|---|---|---|
| `/` | GET | 200 | Service metadata |
| `/health` | GET | 200 | Health check |
| `/version` | GET | 200 | Worker version |
| `/submit-echo` | GET/POST | 410 | Deprecated — returns tombstone response |
| `*` | any | 404 | Not found |

## Configuration

Only `ALLOWED_ORIGINS` (optional) and `WORKER_VERSION` (optional) are read by the current code. No KV, GitHub token, or Turnstile is required.

```bash
# Optional: set allowed CORS origins (comma-separated)
wrangler secret put ALLOWED_ORIGINS
# Optional: override the hardcoded version string
wrangler secret put WORKER_VERSION
```

Deploy:

```bash
wrangler deploy
```

## Verify deployment

```bash
./scripts/check-live-worker.sh https://<your-worker-name>.<your-subdomain>.workers.dev
```

Expected:

- `GET /health` → `200`
- `GET /version` → `200`
- `GET /submit-echo` → `410`
- Response header contains `X-Echo-Worker-Version`
