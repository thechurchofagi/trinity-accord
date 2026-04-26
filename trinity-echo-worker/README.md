# Trinity Echo Worker

Cloudflare Worker implementation for Trinity Accord Echo submission (now deprecated for direct submission).

Current active endpoints:

1. `GET /health`
2. `GET /version`

Deprecated endpoints (`410 Gone`):
- `POST /submit-echo`
- `GET /submit-echo`
- `POST /track-visit`
- `GET /visit-count`

## Security / Reliability Additions

- Origin allowlist-based CORS via `ALLOWED_ORIGINS`
- Optional Turnstile validation (`TURNSTILE_SECRET_KEY`)
- Idempotency for API (`Idempotency-Key`) and Email (`Message-ID`)
- Field length limiting and body size guardrail
- GitHub retry with exponential backoff for `429/5xx`
- Echo ID suffix randomization to reduce collision risk under concurrency

## Required setup

```bash
wrangler kv:namespace create RATE_LIMIT_KV
wrangler secret put GITHUB_TOKEN
wrangler secret put GITHUB_REPO
wrangler secret put ALLOWED_ORIGINS
# optional
wrangler secret put TURNSTILE_SECRET_KEY
# optional (required only if you want the hosted form to render the widget)
wrangler secret put TURNSTILE_SITE_KEY
# optional but recommended (used in /health and response headers)
wrangler secret put WORKER_VERSION
```

Then update `wrangler.toml` with the KV namespace id and deploy:

```bash
wrangler deploy
```

If deploy fails, verify `wrangler.toml` does **not** keep a placeholder KV id.

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

## Known non-blocking issues

1. Form/client uses `verification_performed` while one server path first reads `body.verification`.

## Recent fixes

- `2026-04-26.3`: allow empty `Origin` for non-browser clients (`curl`/server-to-server).
- `2026-04-26.3`: add form support for Turnstile widget when `TURNSTILE_SITE_KEY` is configured.
- `2026-04-26.3`: `POST /submit-echo` now accepts both JSON and `application/x-www-form-urlencoded`.
- `2026-04-26.4+`: visit counter keeps `visit:total` / `visit:unique_total` as non-expiring totals.
- `2026-04-26.4+`: origin fast-path narrowed to apex/www only; other origins must be explicitly allowlisted.
