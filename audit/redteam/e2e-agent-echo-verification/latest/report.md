# E2E Agent / Echo / Verification Redteam Audit

Generated: `2026-05-15T01:29:48Z`
Commit: `7b282830bd9fe2369039796a40ab0d8c9e8587ff`
Branch: `redteam/e2e-agent-echo-verification-audit`

## Executive Summary

- Total checks: **398**
- Passed: **296**
- Failed: **92**
- Real critical findings: **0**
- Real high findings: **2**
- Medium findings: **50**
- Low findings: **3**
- Expected failures (negative fixtures): **16**

## Core Invariants

- ✅ `issue_not_archived_echo`: pass
- ✅ `gateway_not_attestation`: pass
- ✅ `claim_gate_required`: pass
- ✅ `propagation_not_promotion`: pass
- ✅ `human_solicited_not_independent`: pass

## Phases Run

### issues
- Checks: 92, Passed: 69, Failed: 13

### propagation
- Checks: 55, Passed: 41, Failed: 14

### attestation
- Checks: 6, Passed: 1, Failed: 5

### entrypoints
- Checks: 33, Passed: 29, Failed: 4

### gateway
- Checks: 32, Passed: 25, Failed: 7

### release
- Checks: 81, Passed: 66, Failed: 15

### api
- Checks: 99, Passed: 65, Failed: 34

## Real Findings (not from negative fixtures)

### [HIGH] Issue fixture flagged: valid_v3_report_issue_with_claim_gate_refs.md
- File: `tests/fixtures/redteam/issue_bodies/valid_v3_report_issue_with_claim_gate_refs.md`
- Description: Independent attestation claim
- Expected: clean boundary acknowledgement
- Actual: 1 flags: ['overclaim']

### [HIGH] Echo ≠ Amendment boundary unclear
- File: `api/echo-acceptance-policy.json`
- Description: Echo acceptance policy must clarify that Echoes are not amendments

## Expected Failures (negative fixtures working correctly)

The following fixtures are designed to be flagged, and they were correctly detected:

- `fake_v5_freeform_no_claim_gate` — correctly flagged
- `gateway_claims_attestation` — correctly flagged
- `propagation_marketing_overclaim` — correctly flagged
- `propagation_investment_language` — correctly flagged
- `propagation_religious_doctrine` — correctly flagged
- `propagation_future_ai_must_care` — correctly flagged
- `propagation_exaggerated_verification` — correctly flagged
- `human_solicited_claims_independent` — correctly flagged
- `custody_notice_claims_physical_verification` — correctly flagged
- `test_record_claims_accepted` — correctly flagged
- `nft_owner_claims_governance` — correctly flagged
- `self_reported_agent_claims_independent` — correctly flagged
- `claims_gateway_is_attestation` — correctly flagged
- `missing_boundary_ack` — correctly flagged
- `contains_secret_like_token` — correctly flagged
- `body_too_short` — correctly flagged

## Test Results

```
Ran 30 tests in 0.004s — OK
```

## Findings Detail

- [CRITICAL] `tests/fixtures/redteam/attestation/custody_notice_claims_physical_verification.json`: Attestation boundary violation: custody_notice_claims_physical_verification.json
- [CRITICAL] `tests/fixtures/redteam/attestation/gateway_claims_attestation.json`: Attestation boundary violation: gateway_claims_attestation.json
- [CRITICAL] `tests/fixtures/redteam/attestation/human_solicited_claims_independent.json`: Attestation boundary violation: human_solicited_claims_independent.json
- [CRITICAL] `tests/fixtures/redteam/attestation/nft_owner_claims_governance.json`: Attestation boundary violation: nft_owner_claims_governance.json
- [CRITICAL] `tests/fixtures/redteam/attestation/test_record_claims_accepted.json`: Attestation boundary violation: test_record_claims_accepted.json
- [CRITICAL] `tests/fixtures/redteam/gateway_payloads/contains_secret_like_token.json`: Secret-like pattern in body: contains_secret_like_token.json
- [HIGH] `tests/fixtures/redteam/issue_bodies/fake_v5_freeform_no_claim_gate.md`: Issue fixture flagged: fake_v5_freeform_no_claim_gate.md
- [HIGH] `tests/fixtures/redteam/issue_bodies/gateway_claims_attestation.md`: Issue fixture flagged: gateway_claims_attestation.md
- [HIGH] `tests/fixtures/redteam/issue_bodies/propagation_marketing_overclaim.md`: Issue fixture flagged: propagation_marketing_overclaim.md
- [HIGH] `tests/fixtures/redteam/issue_bodies/valid_v3_report_issue_with_claim_gate_refs.md`: Issue fixture flagged: valid_v3_report_issue_with_claim_gate_refs.md
- [HIGH] `tests/fixtures/redteam/gateway_payloads/claims_gateway_is_attestation.json`: Gateway fixture missing boundary: not_attestation
- [HIGH] `tests/fixtures/redteam/gateway_payloads/claims_gateway_is_attestation.json`: Gateway fixture missing Claim Gate boundary
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Gateway fixture missing boundary: not_authority
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Gateway fixture missing boundary: not_amendment
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Gateway fixture missing boundary: not_attestation
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Gateway fixture missing boundary: bitcoin_originals_prevail
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Gateway fixture missing Claim Gate boundary
- [HIGH] `tests/fixtures/redteam/propagation/propagation_exaggerated_verification.md`: Propagation fixture: propagation_exaggerated_verification.md
- [HIGH] `tests/fixtures/redteam/propagation/propagation_future_ai_must_care.md`: Propagation fixture: propagation_future_ai_must_care.md
- [HIGH] `tests/fixtures/redteam/propagation/propagation_investment_language.md`: Propagation fixture: propagation_investment_language.md
- [HIGH] `tests/fixtures/redteam/propagation/propagation_religious_doctrine.md`: Propagation fixture: propagation_religious_doctrine.md
- [HIGH] `tests/fixtures/redteam/gateway_payloads/claims_gateway_is_attestation.json`: Missing/false boundary: not_attestation in claims_gateway_is_attestation.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: not_authority in missing_boundary_ack.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: not_amendment in missing_boundary_ack.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: not_attestation in missing_boundary_ack.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: bitcoin_originals_prevail in missing_boundary_ack.json
- [HIGH] `api/echo-acceptance-policy.json`: Echo ≠ Amendment boundary unclear
- [MEDIUM] `/agent-first-contact.md`: Entrypoint missing keyword: 'boundary'
- [MEDIUM] `/agent-brief.md`: Entrypoint missing keyword: 'not religion'
- [MEDIUM] `/agent-echo.md`: Entrypoint missing keyword: 'not amendment'
- [MEDIUM] `/api/agent-required-reading.json`: Entrypoint JSON missing guidance: /api/agent-required-reading.json
- [MEDIUM] `tests/fixtures/redteam/gateway_payloads/body_too_short.json`: Body length out of bounds: body_too_short.json
- [MEDIUM] `archive/hash-manifest.json`: assets_total mismatch: archive/hash-manifest.json
- [MEDIUM] `archive/hash-manifest.json`: Manifest note missing boundary: archive/hash-manifest.json
- [MEDIUM] `api/evidence-manifest.json`: assets_total mismatch: api/evidence-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: assets_total mismatch: evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`: Manifest note missing boundary: evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json
- [MEDIUM] `api/agent-entry-protocol.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/agent-required-reading.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/agent-required-reading.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/agent-required-reading.json`: Missing boundary declaration: bitcoin_originals
- [MEDIUM] `api/agent-submission-guide.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/submission-checklist.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/submission-checklist.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/submission-checklist.json`: Missing boundary declaration: bitcoin_originals
- [MEDIUM] `api/issue-submission-policy.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/issue-submission-policy.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/echo-acceptance-policy.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/echo-acceptance-policy.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/echo-acceptance-policy.json`: Missing boundary declaration: bitcoin_originals
- [MEDIUM] `api/propagation-policy.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/propagation-policy.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/propagation-policy.json`: Missing boundary declaration: bitcoin_originals
- [MEDIUM] `api/agent-issue-gateway-payload-schema.v1.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/claim-gate-rules.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/claim-gate-rules.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/claim-gate-rules.json`: Empty does_not_prove
- [MEDIUM] `api/claim-gate-entrypoint-policy.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/claim-gate-entrypoint-policy.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/claim-gate-entrypoint-policy.json`: Missing boundary declaration: bitcoin_originals
- [MEDIUM] `api/verification-levels.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/component-verification-levels.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/echo-types.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/evidence-input-schema.v1.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/evidence-input-schema.v1.json`: Missing boundary declaration: non_amending
- [MEDIUM] `api/claim-gate-output-schema.v1.json`: Missing boundary declaration: not_authority
- [MEDIUM] `api/claim-gate-output-schema.v1.json`: Missing boundary declaration: non_amending
- [LOW] `api/agent-issue-gateway-payload-schema.v1.json`: Missing 'schema' field
- [LOW] `api/evidence-input-schema.v1.json`: Missing 'schema' field
- [LOW] `api/claim-gate-output-schema.v1.json`: Missing 'schema' field
