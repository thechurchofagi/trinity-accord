# Repository Size Policy

> This document describes the Trinity Accord repository size management strategy.

## Current status

| Metric | Value |
|--------|-------|
| `.git` (pack) | ~66 MiB |
| Working tree | ~47 MiB |
| Tracked files | 977 |
| Largest current file | ~4.6 MiB (evidence JPG) |
| Largest historical blob | 23.1 MiB (removed `public-covenant-archive.zip`) |

## Principles

1. **Git is for text, manifests, and scripts — not for large binaries.**
   Large evidence payloads (ZIP, high-res images, video) belong in GitHub Release, Arweave, or IPFS. Git should only store SHA-256 hashes, metadata, and verification scripts.

2. **Evidence integrity is non-negotiable.**
   No file in `archive/`, `evidence/`, or any trust-root path may be deleted or moved without explicit maintainer approval and a documented migration plan.

3. **Shallow clone is the default for consumers.**
   Most users and agents do not need full Git history. Use:

   ```bash
   git clone --depth=1 https://github.com/thechurchofagi/trinity-accord.git
   ```

4. **History rewrite is last resort.**
   `git filter-repo` or BFG rewrites all commit SHAs, which may break provenance references, external audits, and tag continuity. It is only considered when:
   - Historical blobs dominate `.git` size (>50%)
   - Project is early-stage with few external forks
   - Maintainer explicitly approves with a migration notice

## Large file threshold

CI enforces a **5 MiB** threshold on tracked files. Any file exceeding this triggers a warning and requires maintainer review before merge.

## Evidence JPG audit (2026-05-15)

The 10 JPG files in `evidence/notarial-certificate-2026-05-13/公证书/` total **38 MiB**. They are:

- Not rendered by any site page or API endpoint
- Not included in any external manifest (Release, Arweave, IPFS)
- Referenced only by `证据保全公证完整档案.md` with SHA-256 checksums

**Recommendation:** Migrate to GitHub Release or Arweave; replace Git copies with manifest entries. This is a maintainer decision, not an automated action.

## Related files

- `RELEASE-LARGE-DATA-MANIFEST.json` — externalized large assets
- `archive/hash-manifest.json` — archive hash records
- `api/evidence-manifest.json` — evidence manifest
- `audit/repo-size/` — audit reports
