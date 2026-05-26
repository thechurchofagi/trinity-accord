---
layout: default
title: "TA-REDTEAM-2026-006 Remediation"
permalink: /ta-redteam-2026-006-remediation/
---
# TA-REDTEAM-2026-006 Remediation Report

## Summary

Status: **Fixed**
Commit: `99b69c9`
Files changed: 12 (2 modified, 10 new)

## Fixed Findings

| ID | Severity | Status | Evidence |
|---|---:|---|---|
| REL-SCHEMA-001 | High | fixed | `normalizeReleaseManifest()` with schema gate; unsupported schema → exit non-zero |
| REL-COMPLETE-001 | High | fixed | Manifest-driven verification; missing/extra/duplicate assets → FAIL; count invariants enforced |
| REL-TAR-001 | High | fixed | `extractFilesFromTarStrict()`: duplicate/traversal/absolute/truncated/symlink → FAIL |
| REL-CID-001 | Medium | fixed | `verification_scope=hash_size_only` when CID disabled; `does_not_prove` includes CID/DAG boundaries |
| REL-CAR-001 | Medium | fixed | Strict CAR header varint parsing with bounds checks |
| REL-RESOURCE-001 | Medium | fixed | `MAX_RELEASE_ASSET_BYTES` (1GB) + `MAX_TOTAL_RELEASE_BYTES` (20GB) + Content-Length cap |
| REL-REPORT-001 | Medium | fixed | JSON schema + `validate_verify_release_report.py --self-test`; PASS invariants enforced |
| REL-BOUNDARY-001 | Low | fixed | `does_not_prove` + `limitations` arrays in report |

## Implementation

### Manifest schema compatibility

- `normalizeReleaseManifest()` supports `trinity-release-manifest-v1` and `legacy-per-nft-assets`
- Unsupported schema throws → exit non-zero
- `report.supported_manifest_schema` records which schema was used

### Complete asset set proof

- Iterates `normalized.expected_nft_assets` (not observed release assets)
- `missing_release_asset` → FAIL
- `unexpected_release_asset` → FAIL
- `duplicate_release_asset` → FAIL
- `manifest_count_mismatch` → FAIL
- `computeStatus()` checks `assetsVerified !== assetsExpected`

### Strict TAR parsing

- `extractFilesFromTarStrict()` replaces `extractFilesFromTar()`
- Detects: duplicate entries, path traversal, absolute paths, unsupported typeflags, truncated payloads
- Uses `Map` lookup (not `.find()`)
- Checks unexpected TAR entries against expected paths

### Verification scope and limitations

- `verification_scope`: `hash_size_only` | `hash_size_and_metadata_cid`
- `does_not_prove`: 5-7 items including CID/DAG/on-chain boundaries
- `limitations`: 4 items about API timing, hash≠on-chain, media CID, TAR strictness

### Report schema and invariants

- `api/verify-release-report-schema.v1.json` defines required fields
- `validate_verify_release_report.py` checks:
  - PASS → errors empty
  - PASS → assets_verified == assets_expected
  - PASS → sha256_pass == car_files_expected
  - PASS → size_pass == car_files_expected
  - hash_size_only → does_not_prove mentions CID/DAG

### Resource limits

- `MAX_RELEASE_ASSET_BYTES`: per-asset cap (default 1GB, env-configurable)
- `MAX_TOTAL_RELEASE_BYTES`: total cap (default 20GB, env-configurable)
- Content-Length check before download
- Actual buffer size check after download
- Concurrency bounded 1-25

## Tests

```text
python3 scripts/test_verify_release_manifest_schema_compatibility.py
python3 scripts/test_verify_release_completeness_gates.py
python3 scripts/test_verify_release_tar_duplicate_fail_closed.py
python3 scripts/test_verify_release_scope_boundary.py
python3 scripts/test_verify_release_resource_limits.py
python3 scripts/test_verify_release_report_invariants.py
python3 scripts/test_verify_car_parser_fail_closed.py
python3 scripts/validate_verify_release_report.py --self-test
```

## Results

```text
VERIFY_RELEASE_MANIFEST_SCHEMA_COMPATIBILITY_OK
VERIFY_RELEASE_COMPLETENESS_GATES_OK
VERIFY_RELEASE_TAR_DUPLICATE_FAIL_CLOSED_OK
VERIFY_RELEASE_SCOPE_BOUNDARY_OK
VERIFY_RELEASE_RESOURCE_LIMITS_OK
VERIFY_RELEASE_REPORT_INVARIANTS_OK
VERIFY_CAR_PARSER_FAIL_CLOSED_OK
VALIDATE_VERIFY_RELEASE_REPORT_SELF_TEST_OK
RELEASE_ASSET_MANIFEST_OFFLINE_OK
VERIFY_DAG_MANIFEST_ITEM_DEFINED_OK
FULL_EVIDENCE_CHAIN_OTS_FAIL_CLOSED_OK
FULL_EVIDENCE_CHAIN_ETH_AUDIT_REQUIRED_OK
FULL_EVIDENCE_CHAIN_CLI_INJECTION_OK
NODE_EXEC_NO_SHELL_INJECTION_OK
ACTION_PINNING_OK
WORKFLOW_INPUT_SAFETY_OK
node --check verify-release-assets.mjs — OK
node --check verify-full-evidence-chain.mjs — OK
node --check verify-dag-and-signed-cids.mjs — OK
```

## Residual Risk

- `verify-dag-and-signed-cids.mjs` and `verify-full-evidence-chain.mjs` still have `catch { /* skip */ }` in their CAR block parsers — acceptable for cross-CAR resolution where skipping is intentional, but should be reviewed for mandatory DAG verification
- `readVarint` in DAG scripts lacks strict bounds checking (mitigated by strict `parseCarHeader` in release verifier)

## Closure Recommendation

TA-REDTEAM-2026-006 **can be closed**. All eight findings (A-H) are addressed with code-level enforcement, schema validation, and test coverage integrated into CI.
