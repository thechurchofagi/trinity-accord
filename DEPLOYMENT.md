# Deployment Checklist (GitHub Pages)

## 1) Pages source
In repository settings:
- Source: **Deploy from a branch**
- Branch: **main**
- Folder: **/(root)**

## 2) Required published paths
- `/.well-known/trinity-accord.json`
- `/api/authority.json`
- `/api/verification-levels.json`
- `/verify`
- `/agent-start`
- `/robots.txt`
- `/sitemap.xml`

## 3) Notes
- This repository uses Markdown + JSON static content.
- `/.well-known` publication depends on `_config.yml` include rules.
- Use `favicon.svg` to avoid binary-file tooling errors in PR pipelines.

## 4) Post-deploy validation
Open site and verify:
- Homepage boundary statement appears.
- Authority and verification pages load.
- Machine-readable JSON endpoints return valid JSON.
