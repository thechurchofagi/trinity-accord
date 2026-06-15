# Record-Chain Repair Inventory — Batch 0

**Date:** 2026-06-15
**Agent:** Automated preflight
**Purpose:** Baseline snapshot before repair batches begin

---

## 1. Files Inspected

### Core Scripts
| File | Lines | Status |
|------|-------|--------|
| `scripts/trinity_record_chain.py` | 1456 | ✅ Present |
| `scripts/record_chain_hashing.py` | 720 | ✅ Present |
| `scripts/build_record_chain_arweave_archive.py` | 534 | ✅ Present |
| `scripts/verify_record_chain_arweave_archive.py` | 357 | ✅ Present |
| `scripts/detect_record_chain_pipeline_backlog.py` | 104 | ✅ Present |
| `scripts/generate_record_chain_status.py` | 369 | ✅ Present |
| `scripts/ots_anchor_native_record_chain_head.py` | — | ✅ Present |
| `scripts/ots_verify_record_chain_anchor.py` | — | ✅ Present |

### Gateway App
| File | Lines | Status |
|------|-------|--------|
| `apps/record_chain_intake_gateway/app.py` | 1365 | ✅ Present |
| `apps/record_chain_intake_gateway/gateway/validation.py` | 1779 | ✅ Present |
| `apps/record_chain_intake_gateway/gateway/authorship.py` | 351 | ✅ Present |
| `apps/record_chain_intake_gateway/gateway/receipts.py` | 132 | ✅ Present |
| `apps/record_chain_intake_gateway/gateway/rate_limit.py` | — | ✅ Present |

### Builder & API
| File | Lines | Status |
|------|-------|--------|
| `downloads/record-chain-builder.mjs` | 2443 | ✅ Present |
| `api/record-chain-submission-schema.v1.json` | — | ✅ Present |
| `api/record-chain-common-field-model.v1.json` | — | ✅ Present |
| `api/record-chain-field-helper.v1.json` | — | ✅ Present |
| `api/record-chain-production-enablement-policy.v1.json` | — | ✅ Present |
| `api/record-chain-status.json` | — | ✅ Present |
| `api/record-chain-arweave-index.json` | — | ✅ Present |
| `api/record-chain-native-ots-latest.json` | — | ✅ Present |

### CI Workflows
| File | Status |
|------|--------|
| `.github/workflows/record-chain-append.yml` | ✅ Present |
| `.github/workflows/record-chain-head-ots-anchor.yml` | ✅ Present |
| `.github/workflows/record-chain-arweave-archive.yml` | ✅ Present |

### Tests
| File | Status |
|------|--------|
| `tests/test_redteam_api_consistency.py` | ✅ Present |
| `tests/test_oath_readback_redaction.py` | ✅ Present |
| `tests/test_record_chain_append_workflow.py` | ✅ Present |
| `tests/test_origin_classification_integration.py` | ✅ Present |
| `tests/test_gateway_context_readiness.py` | ✅ Present |
| `tests/test_evidence_image_manifest.py` | ✅ Present |
| `tests/test_v3plus_signed_coverage_gate.py` | ✅ Present |
| `tests/test_oath_policy_hash_contract.py` | ✅ Present |
| `tests/test_record_chain_write_path_guard.py` | ✅ Present |
| `tests/test_redteam_issue_vs_archive.py` | ✅ Present |
| `tests/test_gateway_hotfix_d.py` | ✅ Present |
| `tests/test_record_chain_guardian_retirement_flow.py` | ✅ Present |
| `tests/verify_shenzhen_notary_archive.py` | ✅ Present |

---

## 2. Baseline Test Results

| Command | Result |
|---------|--------|
| `python3 scripts/trinity_record_chain.py verify` | ✅ PASSED |
| `python3 scripts/verify_record_chain_arweave_archive.py` | ✅ PASSED |
| `python3 scripts/detect_record_chain_pipeline_backlog.py` | ✅ PASSED (pipeline_current=true) |
| `node downloads/record-chain-builder.mjs doctor --help` | ✅ EXIT 0 |
| `python3 -m pytest` | ⚠️ pytest not installed (Python 3.12.3 available) |

---

## 3. Chain State

- **Chain ID:** trinity-accord-public-reception-ledger
- **Native record count:** 43
- **Latest record:** R-000000043
- **Arweave:** matches chain ✅, matches OTS ✅
- **OTS:** matches chain ✅
- **Pipeline current:** true

---

## 4. Key Code Observations (for repair batches)

### A. Boundary fields (Bug #36, #37)
Current `BOUNDARY` dict has **7 fields**, but plan requires **9 fields**:
- Missing: `receipt_is_not_final_inclusion`, `receipt_is_intake_only`, `later_records_may_reclassify_or_correct_this_record`
- Also: `require_boundary()` checks only 6 fields (not `not_verification_level_unless_evidence_backed`)

### B. Authorship exempt types (Bug #1, #38)
`AUTHORSHIP_EXEMPT_TYPES` includes `context_insufficient_notice` — plan says CIN should require authorship proof but not oath.

### C. Final-chain verify (Bug #35)
`verify_native_records()` checks `authorship_verification_status` fields but does **NOT** re-verify Ed2559 signatures against stored `authorship_proof`. Status fields are not cryptographic proof.

### D. Guardian lifecycle (Bug #71, #72)
`build_indexes()` in trinity_record_chain.py derives guardian state — need to check if `guardian_application` can become active directly.

### E. Hash semantics (Bug #68)
`content_sha256` uses `content_hash()` — need to verify it excludes append/server metadata.

### F. Receipt lifecycle (Bug #17, #75)
`receipts.py` is 132 lines — need to verify receipt status tracking and hash verification.

---

## 5. Environment

- **Python:** 3.12.3
- **Node:** v22.22.1
- **Git:** 2.43.0
- **OS:** Linux 6.8.0-100-generic (x64)
- **pytest:** Not installed (pip3 available)

---

## 6. Known Pre-existing Issues

- pytest not installed in sandbox (can install via pip3 if needed for test validation)
- No other pre-existing failures detected in baseline commands
