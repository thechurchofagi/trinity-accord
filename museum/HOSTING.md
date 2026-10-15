# Museum hosting — GitHub Pages

Canonical address: https://www.trinityaccord.org/museum/

GitHub `thechurchofagi/trinity-accord`, directory `museum/`, is the only maintained source. The existing main-site Deploy Pages workflow copies the complete, unprocessed `museum/dist/` export into `_site/museum/` and verifies its inventory and SHA-256 digests. The main site's custom domain remains unchanged.

## Migration on 2026-10-15

The owner retired the unpaid Alibaba Cloud server. The old `museum.trinityaccord.org` address is no longer the public entry. Entry HTML and the generated reading archive no longer redirect there. Homepage navigation, canonical URLs, sitemap and the museum IndexNow configuration point to the Pages location.

No DNS change is required for the new address. The old subdomain cannot redirect visitors while its server is offline; update bookmarks to the canonical address. Do not claim old-domain recovery without a separate verified DNS/hosting cutover. The former server configuration is retained only in `history/HOSTING-aliyun-retired.md`.

## Publish and verify

1. Keep all runtime, media, JSON and vendor files in `dist/`. The browser executes the 3D scene; there is no museum backend.
2. For runtime changes, follow the existing build instructions in README. For address-only changes, regenerate the reading archive/inventory with `python3 museum/scripts/build_archive.py`.
3. Run `python3 museum/scripts/validate.py`. Review the exact changed files; all original media should remain unchanged for this migration.
4. Publish the reviewed current main revision using the existing Deploy Pages workflow. A commit containing `[skip ci]` needs a separate deployment dispatch; a source commit alone is not publication.
5. Verify https://www.trinityaccord.org/museum/ and `archive.html`, then use `python3 scripts/smoke_live_museum.py` for byte-level export verification. Check the homepage Museum link, model loading, recorded guide, music, subtitles and mobile controls. Record any unavailable browser verification explicitly.

Use relative resource paths. The service worker is registered with `scope: './'`; its cache namespace derives from its own path, so the Pages cache is confined to `/museum/`. HTML and runtime scripts are not stored in the media cache. Audio byte ranges and network fallback remain supported by the existing worker.

## Rollback and preservation

Retain the complete export and Git history. Roll back content to a reviewed snapshot while retaining the working Pages address; do not reintroduce a redirect to the retired server. Validate the regenerated inventory and redeploy. External provenance links remain external, while the scene, exhibition images, music and recorded guide are bundled locally.
