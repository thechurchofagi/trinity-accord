# Security Headers Configuration

> Trinity Accord is hosted on GitHub Pages, which does not support custom HTTP headers directly.
> Security headers must be configured at the CDN/reverse-proxy layer (e.g., Cloudflare).

## Recommended headers

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
X-Content-Type-Options: nosniff
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=(), payment=()
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'; img-src 'self' data: https:; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; upgrade-insecure-requests
```

## Configuration locations

| Platform | Method |
|---|---|
| Cloudflare | Dashboard → Security → Headers, or Transform Rules |
| Netlify | `_headers` file in publish directory |
| Vercel | `vercel.json` headers array |
| Nginx reverse proxy | `add_header` directives in server block |
| GitHub Pages | Not supported directly; requires CDN layer |

## Verification

```bash
curl -sI https://www.trinityaccord.org | grep -iE 'strict-transport|x-content-type|referrer-policy|permissions-policy|x-frame|content-security'
```

## CSP notes

- `unsafe-inline` for styles is required by Jekyll themes.
- `unsafe-inline` for scripts may be tightened after auditing inline scripts.
- `upgrade-insecure-requests` ensures HTTP resources redirect to HTTPS.
- `frame-ancestors 'none'` prevents clickjacking.

## Status

- [ ] Headers configured at CDN/proxy layer
- [ ] Verified with线上 HEAD request
- [ ] CSP audit completed
