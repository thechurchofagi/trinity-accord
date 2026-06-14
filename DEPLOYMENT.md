# Deployment Checklist (GitHub Pages)

## 1) GitHub Pages deployment mode

Current production deployment uses GitHub Actions artifact deployment.

Canonical workflow:

- `.github/workflows/deploy-pages.yml`
- builds Jekyll output into `_site`
- restores committed static API and builder artifacts into `_site`
- verifies public agent JSON entrypoints
- uploads the Pages artifact
- deploys with `actions/deploy-pages`

Do not configure production Pages as plain branch/root deployment unless this repository intentionally reverts to the legacy deployment mode.

Legacy fallback: branch/root deployment is historical documentation only and must not bypass `deploy-pages.yml` checks.

## 2) Required published paths
- `/.well-known/trinity-accord.json`
- `/api/authority.json`
- `/api/verification-levels.json`
- `/verify`
- `/agent-start`
- `/robots.txt`
- `/sitemap.xml`
- `/favicon.ico`

## 3) Notes
- This repository uses Markdown + JSON static content.
- `/.well-known` publication depends on `_config.yml` include rules.
- Use `favicon.svg` to avoid binary-file tooling errors in PR pipelines.

## 4) Post-deploy validation
Open site and verify:
- Homepage boundary statement appears.
- Authority and verification pages load.
- Machine-readable JSON endpoints return valid JSON.


## 5) Favicon endpoint check
- `/favicon.ico` endpoint should return HTTP 200 after deploy.
