---
layout: default
title: "TA-REDTEAM-2026-006 Followup Remediation"
---
# TA-REDTEAM-2026-006 Follow-up Remediation Report

## Summary

Status: **Fixed**
Commit: `1814a28`
Files changed: 8 (5 modified, 2 new)

## Fixed Blocking Issues

| ID | Severity | Status | Evidence |
|---|---:|---|---|
| REL-SCHEMA-001 | High | fixed | `download-nft-cars.mjs` generates `RELEASE-MANIFEST.json` (schema `trinity-release-manifest-v1`); `verify-release-assets.mjs` normalizes both `per_nft_assets` and `release_assets` schemas |
| REL-CAR-001 | Medium | fixed | `readVarintStrict` with bounds/overlong/safe-integer checks; `blockEnd > data.length` throws; no `catch { /* skip */ }` in mandatory paths; malformed root/block/link CID throws; duplicate CID conflict detection |

## Implementation

### Producer/consumer release manifest compatibility

- **Producer output**: `download-nft-cars.mjs` now generates `RELEASE-MANIFEST.json` with `schema: trinity-release-manifest-v1`
- **Schema**: Groups verified CAR files by contract+tokenId into `per_nft_assets` entries
- **Upload**: `RELEASE-MANIFEST.json` uploaded as Release asset before tar parts
- **Verifier**: `verify-release-assets.mjs` `normalizeReleaseManifest()` supports both `per_nft_assets` and `release_assets` (part-based) schemas
- **Compatibility**: Producer-style manifest tested end-to-end with Node.js import test

### DAG/CAR parser fail-closed

- **readVarintStrict**: Max 10 iterations, bounds check, safe integer check, overlong detection
- **consumeVarint**: Helper for bounds-checked varint consumption in CID parsing
- **parseCarFull**: `blockEnd > data.length` throws (was `break`); no silent catch
- **extractRootsFromHeader**: Malformed root CID throws (was silent skip)
- **extractLinksFromBlock**: Malformed CID link throws (was silent skip)
- **Duplicate CID**: Conflict detection — same CID with different data throws
- **Both scripts**: Applied to `verify-dag-and-signed-cids.mjs` and `verify-full-evidence-chain.mjs`
- **Test**: `test_verify_car_parser_fail_closed.py` now hard-fails on old weak patterns

## Tests

```text
python3 scripts/test_download_nft_cars_release_manifest_v1.py
python3 scripts/test_verify_release_assets_consumes_nft_cars_manifest.py
python3 scripts/test_verify_car_parser_fail_closed.py
python3 scripts/test_verify_release_manifest_schema_compatibility.py
python3 scripts/test_verify_release_completeness_gates.py
python3 scripts/test_verify_release_tar_duplicate_fail_closed.py
python3 scripts/test_verify_release_scope_boundary.py
python3 scripts/test_verify_release_resource_limits.py
python3 scripts/test_verify_release_report_invariants.py
python3 scripts/validate_verify_release_report.py --self-test
```

## Results

```text
DOWNLOAD_NFT_CARS_RELEASE_MANIFEST_V1_OK
VERIFY_RELEASE_ASSETS_CONSUMES_NFT_CARS_MANIFEST_OK
VERIFY_CAR_PARSER_FAIL_CLOSED_OK
VERIFY_RELEASE_MANIFEST_SCHEMA_COMPATIBILITY_OK
VERIFY_RELEASE_COMPLETENESS_GATES_OK
VERIFY_RELEASE_TAR_DUPLICATE_FAIL_CLOSED_OK
VERIFY_RELEASE_SCOPE_BOUNDARY_OK
VERIFY_RELEASE_RESOURCE_LIMITS_OK
VERIFY_RELEASE_REPORT_INVARIANTS_OK
VALIDATE_VERIFY_RELEASE_REPORT_SELF_TEST_OK
RELEASE_ASSET_MANIFEST_OFFLINE_OK
VERIFY_DAG_MANIFEST_ITEM_DEFINED_OK
FULL_EVIDENCE_CHAIN_OTS_FAIL_CLOSED_OK
FULL_EVIDENCE_CHAIN_ETH_AUDIT_REQUIRED_OK
FULL_EVIDENCE_CHAIN_CLI_INJECTION_OK
NODE_EXEC_NO_SHELL_INJECTION_OK
ACTION_PINNING_OK
WORKFLOW_INPUT_SAFETY_OK
node --check download-nft-cars.mjs — OK
node --check verify-release-assets.mjs — OK
node --check verify-dag-and-signed-cids.mjs — OK
node --check verify-full-evidence-chain.mjs — OK
```

## Residual Risk

None identified for the two blocking issues. Both are fully closed with code enforcement and test coverage.

## Closure Recommendation

TA-REDTEAM-2026-006 **can be closed**. All findings (REL-SCHEMA-001 through REL-BOUNDARY-001) are addressed with fail-closed enforcement, producer/consumer compatibility, strict CAR/DAG parsing, and CI-integrated tests.
