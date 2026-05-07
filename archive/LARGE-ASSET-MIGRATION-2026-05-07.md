# Large Asset Migration to GitHub Release — 2026-05-07

## Summary

Large evidence payloads were migrated out of Git history and into GitHub Release assets, then repository history was rewritten to reduce clone size.

## Repository size

| Metric | Before | After (fresh clone) |
|--------|--------|---------------------|
| `.git` | ~79 MB | 1.9 MB |
| Total | ~198 MB | 10 MB |
| **Reduction** | | **~97.6%** |

## Removed from Git

- `archive/evidence/flaw-archive-bundle.zip` (~44 MB)
- `arweave-backup/files/public_covenant_archive.zip` (~24 MB)
- `archive/evidence/flaw-images/指纹/*.jpg` (11 files, ~46 MB)

## Release

- **Tag:** `trinity-accord-large-assets-v1`
- **URL:** https://github.com/thechurchofagi/trinity-accord/releases/tag/trinity-accord-large-assets-v1
- **Assets:**
  - `flaw-archive-bundle.zip`
  - `public_covenant_archive.zip`
  - `flaw-fingerprint-images-2025-06-29.zip`
  - `flaw-fingerprint-images-2025-06-29.payload.sha256`
  - `trinity-accord-large-assets-v1-manifest.json`
  - `trinity-accord-large-assets-v1-assets.sha256`

## Manifest state

- `archive/hash-manifest.json`
  - `release_assets_total: 3`
  - `release_assets_verified: 3`
  - `arweave_assets_total: 0`

- `api/evidence-manifest.json`
  - `primary_storage_domain: github_release`
  - Large asset nodes present for: `flaw_archive_bundle`, `public_covenant_archive`, `flaw_fingerprint_images_2025_06_29`

## Validation

```
NO_FORBIDDEN_LARGE_PATHS_TRACKED_OK
LARGE_ASSET_STORAGE_POLICY_OK
ASSET_MANIFEST_DOMAIN_CONSISTENCY_OK
EVIDENCE_MANIFEST_STATS_SYNC_OK
RELEASE_ASSET_MANIFEST_OFFLINE_OK
```

All source and non-source validation checks passed.

## Collaborator action required

**History was rewritten.** Please re-clone the repository or hard reset to the new `main`. Do not merge old branches containing removed blobs.

## Anti-regression

- `.gitignore` blocks re-addition of large asset paths
- `test_no_forbidden_large_paths_tracked.py` guards against tracked forbidden paths
- `test_large_asset_storage_policy.py` blocks any new file > 5 MB
- CI workflow (`repository-integrity.yml`) enforces both tests on every push
