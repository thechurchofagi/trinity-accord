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
```

Then update `wrangler.toml` with the KV namespace id and deploy:

```bash
wrangler deploy
```
