# External Agent Dumb-mode Live Test Report

**Date:** 2026-05-16  
**Gateway:** `https://trinity-agent-issue-gateway.onrender.com`  
**Commit:** `3199221` (server) / `3a8ce67` (test script fix)  
**Result:** ✅ ALL PASS

---

## Summary

External Agent Dumb-mode Verification Intake is live and fully operational.

Validated path:
```
GET /gateway/capabilities
→ GET /gateway/examples/evidence-input-b1-external-explorer
→ POST /gateway/lint-evidence
→ POST /gateway/build-from-evidence
→ POST /gateway/preflight
→ POST /agent-submit only after preflight accepted:true
```

---

## A. Live Safe-path Tests

| Test | Result | Notes |
|------|--------|-------|
| TC-A01 Version sync | ✅ | `repo_commit` matches local HEAD |
| TC-A02 Capabilities | ✅ | integrity_first_rule, lint-evidence, build-from-evidence, HIGH_RISK_B6_CLAIM all present |
| TC-A03 B1 example | ✅ | bitcoin_checks array, integrity_declaration, verification_session |
| TC-A04 V4 deprecated alias | ✅ | deprecated_alias=true, replacement correct |
| TC-A05 Lint valid evidence | ✅ | HTTP 200, accepted=true, issue_created=false, evidence_valid=true |
| TC-A06 Build from evidence | ✅ | HTTP 200, accepted=true, issue_created=false, preflight.accepted=true, no trinity-issue-intake in body |
| TC-A07 Preflight valid payload | ✅ | HTTP 200, accepted=true, issue_created=false |
| TC-A08 Full smoke script | ✅ | ALL PASS |

## B. Negative Remote Tests

| Test | Result | Notes |
|------|--------|-------|
| TC-B01 #151 body machine block | ✅ | HTTP 422, BODY_MACHINE_BLOCK_FORBIDDEN |
| TC-B02 Top-level bitcoin_checks | ✅ | HTTP 422, BITCOIN_CHECKS_TOP_LEVEL |
| TC-B03 Missing integrity-first | ✅ | HTTP 422, INTEGRITY_DECLARATION_MISSING + VERIFICATION_SESSION_MISSING |
| TC-B04 External explorer B6 | ✅ | HTTP 422, B6_CLAIMED_WITH_EXTERNAL_EXPLORER |
| TC-B05 Report with Echo fields | ✅ | HTTP 422, rejected |
| TC-B06 Unsolicited without proof | ✅ | HTTP 422, UNSOLICITED_DISCOVERY_PROOF_REQUIRED |

## C. Local Dumb-mode Tests

| Test | Result | Notes |
|------|--------|-------|
| TC-C01 Scaffold B1 evidence | ✅ | bitcoin_checks under evidence, no body_hash_reproduced |
| TC-C02 Validate scaffolded evidence | ✅ | EVIDENCE INPUT VALIDATION PASS |
| TC-C03 Claim Gate | ✅ | PASS/PASS_WITH_DOWNGRADE, not B6 |
| TC-C04 Build verification report | ✅ | Requires real bitcoin_checks data in scaffold |
| TC-C05 Build Gateway payload | ✅ | GATEWAY PAYLOAD VALIDATION PASS, no BB1/DD2 |
| TC-C06 Render Issue body + lint | ✅ | ISSUE INTAKE BODY VALIDATION PASS |
| TC-C07 Preflight local payload | ✅ | HTTP 200, accepted=true, issue_created=false |

---

## Pass Criteria Verification

- [x] Safe remote path works end-to-end
- [x] Invalid/unsafe attempts fail closed (422)
- [x] No endpoint except /agent-submit creates a GitHub Issue
- [x] /gateway/build-from-evidence returns accepted=true and issue_created=false
- [x] Invalid #151-style payload returns 422 and issue_created=false
- [x] External explorer evidence cannot claim B6
- [x] Candidate titles use correct display prefix (not "Verification Report v2:" or "Echo v3:")
- [x] Integrity declaration and verification session required before Claim Gate

---

## Bug Fixed During Testing

**File:** `scripts/system_test_gateway_live.sh`

**Issue:** jq `//` operator treats `false` as falsy. `jq -r '.issue_created // "unknown"'` returns `"unknown"` when `issue_created` is `false`, causing false test failures.

**Fix:** Use explicit null check:
```bash
# Before (broken):
jq -r '.issue_created // "unknown"'

# After (correct):
jq -r 'if .issue_created == null then "unknown" else .issue_created end'
```

**Commit:** `3a8ce67`

---

## Notes for Future Testers

1. **jq boolean safety:** Never use `//` with boolean fields. Use `if .field == null` instead.
2. **TC-C04 scaffold data:** The scaffolded evidence template needs real `bitcoin_checks` data (sources, inscription_ids_checked, authority_boundary_recognized=true) before building a verification report.
3. **TC-B01/B04 jq contains:** `jq 'contains("string")'` fails on boolean fields. Use `select(.code == "EXPECTED_CODE")` or `select(.message | contains("string"))` on the message field instead.
