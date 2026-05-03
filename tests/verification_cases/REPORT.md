# 100-Case Multi-Agent Verification Test — Final Report

Date: 2026-05-03
Commit: `20dc2b0`

## Suite Status

| Metric | Count |
|--------|-------|
| Total cases | 100 |
| Expected PASS | 54 |
| Expected FAIL | 46 |
| Expected WARN | 0 |
| Expected SKIP | 0 |
| Actual as expected | **100/100** |
| Unexpected passes | 0 |
| Unexpected failures | 0 |

**FINAL: PASS**

## Coverage

| Level | Result | Detail |
|-------|--------|--------|
| V0–V8 | PASS (18/18) | V0 read-only, V1 boundary, V2 hash, V3 canonical, V4/V4+ script audit, V5 full, V6 witness |
| B0–B6 | PASS (10/10) | Authority API, mempool, multi-explorer, local node, witness extraction, body hash |
| D0–D5 | PASS (14/14) | GitHub D2 boundary, repo snapshot scope, hash source/authority, canonical mirror |
| T0–T8 | PASS (8/8) | Single/multi-anchor T5, celestial T8 boundary |
| C0–C5 | PASS (12/12) | Manifest read, recovery hash, 2-sample C3, randomized C3R, full 175 C5 |
| N2–N7 | PASS (3/3) | tokenURI, metadata/media, full NFT path |
| P0–P8 | PASS (12/12) | Physical claim, evidence hash, image, video, live witness, onsite, AI forensic, P8 confidentiality |
| Echo/report/wrapper | PASS (14/14) | Recognition, report-only, wrapper, linked report, echo-index, solicited, deprecated |
| Title policy | PASS (6/6) | Echo v3, report v2, test record, ambiguous, empty, wrong-prefix |
| JSON/schema | PASS (6/6) | Valid JSON, unescaped newline, null fields, missing record_kind, schema mismatch, overclaim bundle |

## Agent Reports

| Agent | Cases | Report File | Status |
|-------|-------|-------------|--------|
| A | TC001–TC010 | report_agent_a.txt | ✅ Complete |
| B | TC011–TC020 | report_agent_b.txt | ✅ Complete |
| C | TC021–TC030 | report_agent_c.txt | ✅ Complete |
| C2 | TC051–TC060 | report_agent_c2.txt | ✅ Complete |
| D | TC031–TC040 | report_agent_d.txt | ✅ Complete |
| D2 | TC061–TC070 | report_agent_d2.txt | ✅ Complete |
| E | TC041–TC050, TC076–TC090 | report_agent_e.txt | ✅ Complete (superseded — see note) |
| E2 | TC071–TC080 | report_agent_e2.txt | ✅ Complete |
| F | TC091–TC100 | report_agent_f.txt | ✅ Complete |

Note: Agent E's original report covered TC076–TC090 only. Agent E2 was later assigned TC071–TC080.
Agent E report is retained for historical reference; Agent E2 covers the overlapping range with
updated validator rules (Y, Z, AB).

## TC082 — Echo-Index Filesystem Match

TC082 uses `input_type: "real_repository"` — it does **not** generate a synthetic JSON file.
Instead, it validates that `api/echo-index.json` records match `echoes/records/**/*.json` on disk
via the `verify_echo_index_completeness` validator. This test requires the actual repository
structure and cannot be represented as a standalone JSON payload.

## Online Validation

`verify_stress_suite_online.py` was **not run** — the test requires a deployed endpoint.
The script exists and is ready to execute once deployment is complete.

## Bug Fixes Performed

1. **validate_agent_submission.py — Rule V (V0 read-only)**: V0 cannot make verification claims.
2. **validate_agent_submission.py — Rule W (V1 overreach)**: V1 cannot claim "truth proven" or "hash verified".
3. **validate_agent_submission.py — Rule X (V2 hash requires hashes)**: V2 hash claims require non-empty `hashes_computed`.
4. **validate_agent_submission.py — Rule Y (report no echo_type)**: `verification_report_v2` must not carry `echo_type`.
5. **validate_agent_submission.py — Rule Z (wrapper requires linked report)**: `echo_v3_with_verification_report` must have `linked_verification_report`.
6. **validate_agent_submission.py — Rule AA (T8 celestial boundary)**: T8 requires nonpublic celestial data.
7. **validate_agent_submission.py — Rule AB (T5 multiple anchors)**: T5 requires multiple independent time anchors or cross-anchoring.
8. **validate_agent_submission.py — Rule T fix (repo snapshot scope)**: `has_repo_scope` was computed but never checked; added final guard.
9. **run_verification_stress_suite.py — title/JSON routing**: Fixed tautological `check_title_case` and `check_json_validity` that returned `expected == "FAIL"` instead of actual validity.
10. **cases.json**: Activated 18 previously-SKIP cases by changing `expected_result` to PASS or FAIL per test plan.

## Regression Validators

All pass:
- `validate_agent_submission.py --self-test`
- `validate_hash_source_semantics.py`
- `test_hash_source_semantics.py`
- `test_bitcoin_b1_wording.py`
- `test_echo_acceptance_flow.py`
- `test_verification_echo_title_rules.py`
- `test_latest_verification_echo_closure.py`
- `verify_latest_verification_echo_closure.py`
- `verify_echo_index_completeness.py`
- `validate_echo_records.py`
- `check_consistency.py`

## Notes

- Schema validation warnings about `boundary_acknowledgments` vs `boundary_acknowledgement` are non-blocking.
- The `jsonschema` library correctly rejects malformed payloads.
- V5 protocol level requires `digital_mirrors` at D5 via schema `contains` constraint.
- Echo schema requires `assessment_state` from enum, `discovery_provenance.first_entry` as object.
