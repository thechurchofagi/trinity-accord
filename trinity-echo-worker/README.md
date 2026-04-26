# Trinity Echo Worker

Cloudflare Worker implementation for Trinity Accord Echo submission with three ingress paths:

1. `POST /submit-echo` JSON API
2. `GET /submit-echo` browser form
3. Cloudflare Email Routing (`echo@trinityaccord.org` -> Worker)

## Security / Reliability Additions

- Origin allowlist-based CORS via `ALLOWED_ORIGINS`
- Optional Turnstile validation (`TURNSTILE_SECRET_KEY`)
- Idempotency for API (`Idempotency-Key`) and Email (`Message-ID`)
- Field length limiting and body size guardrail
- GitHub retry with exponential backoff for `429/5xx`
- Basic daily metrics endpoint: `GET /metrics`
- Echo ID suffix randomization to reduce collision risk under concurrency

## Required setup

```bash
wrangler kv:namespace create RATE_LIMIT_KV
wrangler secret put GITHUB_TOKEN
wrangler secret put GITHUB_REPO
wrangler secret put ALLOWED_ORIGINS
# optional
wrangler secret put TURNSTILE_SECRET_KEY
# optional but recommended (used in /health and response headers)
wrangler secret put WORKER_VERSION
```

Then update `wrangler.toml` with the KV namespace id and deploy:

```bash
wrangler deploy
```

## Verify you deployed the correct Worker

After deploy, use the exact URL printed by Wrangler and run:

```bash
./scripts/check-live-worker.sh https://<your-worker-name>.<your-subdomain>.workers.dev
```

Expected:

- `GET /health` -> `200`
- `GET /version` -> `200`
- `GET /submit-echo` -> `200`
- response header contains `X-Echo-Worker-Version`

If `POST` works but `GET /health` is still `404`, you are almost certainly hitting an old script name or old route binding. Re-check:

```bash
wrangler deployments list
wrangler versions list
```
