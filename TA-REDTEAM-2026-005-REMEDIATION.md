# TA-REDTEAM-2026-005 Remediation Report

## Summary

Status: **Fixed**
Commit: `ade6d6b`
Files changed: 8 (3 modified, 5 new)

## Fixed Findings

| ID | Severity | Status | Evidence |
|---|---:|---|---|
| 005-A | High | fixed | `verifyDownloadedCarBuffer()` enforces `actual_sha256 == expected_sha256` and `actual_size == expected_size` before any file write or manifest acceptance |
| 005-B | Medium | fixed | Cache path validates via `verifyDownloadedCarBuffer()`; stale cache deleted with `fs.rmSync`; unique tmpdir via `mkdtempSync`; packaging uses `verifiedCarFiles` only |
| 005-C | Medium | fixed | `backup-nft-cars.yml` has sender allowlist for `repository_dispatch` + actor allowlist for `workflow_dispatch`; unauthorized sender exits non-zero |
| 005-D | Low/Medium | fixed | `MAX_CAR_BYTES` (500MB default) per-file cap; `MAX_TOTAL_BYTES` (10GB default) total cap; both expected and actual sizes checked |

## Implementation

### Expected hash / size enforcement

- **helper**: `verifyDownloadedCarBuffer(txid, info, buf, source)` — validates sha256 + size, returns verified manifest item
- **download path**: calls `verifyDownloadedCarBuffer` before `fs.writeFileSync`
- **cached path**: calls `verifyDownloadedCarBuffer` on cached buffer; deletes on mismatch and re-downloads
- **fail behavior**: `fail++`, `verified: false`, failed items excluded from `verifiedCarFiles`

### TMP/cache safety

- **tmp strategy**: `fs.mkdtempSync(path.join(os.tmpdir(), 'nft-cars-'))` — unique per run; or explicit `NFT_CARS_TMP_DIR` cleaned on start
- **verifiedCarFiles packaging**: only files that passed verification enter tar archives

### Manifest

- **expected fields**: `expected_sha256`, `expected_size`
- **actual fields**: `actual_sha256`, `actual_size`
- **match fields**: `sha256_match`, `size_match`, `verified`
- **aggregate checks**: `sha256_check`, `size_check`, `all_expected_sha256_matched`, `all_expected_size_matched`, `all_verified`

### repository_dispatch hardening

- **workflow**: `backup-nft-cars.yml`
- **allowlist**: `thechurchofagi|github-actions[bot]` for `repository_dispatch`; `thechurchofagi` for `workflow_dispatch`

### Resource limits

- **per-file cap**: `MAX_CAR_BYTES` (default 500MB, env-configurable)
- **total cap**: `MAX_TOTAL_BYTES` (default 10GB, env-configurable)

## Tests

```text
python3 scripts/test_download_nft_cars_expected_integrity.py
python3 scripts/test_download_nft_cars_tmp_cache_safety.py
python3 scripts/test_download_nft_cars_manifest_expected_actual.py
python3 scripts/test_backup_nft_cars_dispatch_hardening.py
python3 scripts/test_download_nft_cars_size_limits.py
```

## Results

```text
DOWNLOAD_NFT_CARS_EXPECTED_INTEGRITY_OK
DOWNLOAD_NFT_CARS_TMP_CACHE_SAFETY_OK
DOWNLOAD_NFT_CARS_MANIFEST_EXPECTED_ACTUAL_OK
BACKUP_NFT_CARS_DISPATCH_HARDENING_OK
DOWNLOAD_NFT_CARS_SIZE_LIMITS_OK
DOWNLOAD_NFT_CARS_FAIL_CLOSED_OK
BACKUP_NFT_CARS_INPUT_SAFETY_OK
NODE_EXEC_NO_SHELL_INJECTION_OK
FULL_EVIDENCE_CHAIN_CLI_INJECTION_OK
ACTION_PINNING_OK
WORKFLOW_INPUT_SAFETY_OK
LARGE_ASSET_STORAGE_POLICY_OK
NO_FORBIDDEN_LARGE_PATHS_TRACKED_OK
RELEASE_ASSET_MANIFEST_OFFLINE_OK
node --check scripts/download-nft-cars.mjs — OK
```

## Residual Risk

- Size limits are env-configurable; operators should review defaults for their use case
- `workflow_dispatch` actor allowlist is single-account; expand if more maintainers need access

## Closure Recommendation

TA-REDTEAM-2026-005 **can be closed**. All four sub-findings (A/B/C/D) are addressed with code-level enforcement and test coverage integrated into CI.
