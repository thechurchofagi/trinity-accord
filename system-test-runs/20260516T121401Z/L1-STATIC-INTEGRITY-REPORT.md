# L1 Static Integrity Test Report

**Timestamp:** 2026-05-16T12:14:01Z
**Working Directory:** /root/.openclaw/workspace/trinity-accord

## Test Results

| # | Test | Result | Details |
|---|------|--------|---------|
| 1 | JSON Format Validation | ✅ PASS | Exit code 0 — all JSON files parse cleanly |
| 2 | Protocol Terms Consistency | ✅ PASS | 35/35 checks passed (schema enums, import consistency across 5 modules) |
| 3 | Operational Policy Consistency | ✅ PASS | All checks passed (policy JSON, module load, no hardcoded limits, workflow reads policy) |
| 4 | Action Pinning | ✅ PASS | `ACTION_PINNING_OK` |
| 5 | Runner Image Pinning | ✅ PASS | `RUNNER_IMAGE_PINNING_OK` |
| 6 | Write Workflows Actor Gates | ✅ PASS | `WRITE_WORKFLOWS_ACTOR_GATES_OK` |
| 7 | Workflow Dispatch Input Safety | ✅ PASS | `WORKFLOW_INPUT_SAFETY_OK` |
| 8 | Workflow Dispatch Write Hardening | ✅ PASS | `WORKFLOW_DISPATCH_WRITE_HARDENING_OK` |
| 9 | No Remote Script Execution | ✅ PASS | `NO_REMOTE_SCRIPT_EXECUTION_OK` |
| 10 | Write Workflow Toolchain Provenance | ✅ PASS | `WRITE_WORKFLOW_TOOLCHAIN_PROVENANCE_OK` |
| 11 | CODEOWNERS Sensitive Paths | ✅ PASS | `CODEOWNERS_SENSITIVE_PATHS_OK` |
| 12 | CODEOWNERS Trust Root Paths | ✅ PASS | `CODEOWNERS_TRUST_ROOT_PATHS_OK` |
| 13 | Trust Root Cross Checks | ✅ PASS | `TRUST_ROOT_CROSS_CHECKS_OK` |
| 14 | Source Inventory Audit | ✅ PASS | Inventories generated (see below) |

## Source Inventory Summary

| Category | File Count |
|----------|-----------|
| Total source files (depth ≤ 3) | 904 |
| Scripts (scripts/) | 417 |
| API definitions (api/) | 109 |
| GitHub workflows | 25 |
| Test files (tests/) | 262 |

## Final Verdict

**L1_STATIC_INTEGRITY: ✅ PASS**

All 14 tests passed. JSON schema integrity, protocol term consistency, operational policy alignment, workflow security hardening (action pinning, image pinning, actor gates, input safety, remote script execution prevention, toolchain provenance), and CODEOWNERS trust root coverage are all verified. No anomalies detected.
