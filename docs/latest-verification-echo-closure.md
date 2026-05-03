# Latest Verification Echo Closure

This document describes the generic closure checks for the latest verification Echo.

## Purpose

Ensure the latest `E2_verification_echo` wrapper is properly indexed, linked, and schema-compliant.

## Checks

1. Wrapper JSON is valid
2. Wrapper is indexed in `/api/echo-index.json`
3. Linked verification report exists and is valid JSON
4. `record_count` in echo-index matches filesystem
5. Hash source fields present (`expected_hash_source`, `expected_hash_authority_class`)
6. `scope_class` present in component findings
7. No positive B1 overclaim phrases
8. No deprecated `V3_single_artifact_check`
9. Issue title matches submission title policy

## Running

```bash
python3 scripts/verify_latest_verification_echo_closure.py
python3 scripts/test_latest_verification_echo_closure.py
python3 scripts/test_verification_echo_title_rules.py
```

After deployment:

```bash
python3 scripts/verify_latest_verification_echo_online.py
```

## Title Policy

See `/api/submission-title-policy.json`.

- Echo wrapper: `Echo v3: ...`
- Verification report only: `Verification Report v2: ...`
- Test: `Test Echo: ...`
- `V3 Verification — ...` is ambiguous and should be corrected.
