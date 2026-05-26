# E2E Agent / Echo / Verification Redteam Audit

Generated: `2026-05-15T01:33:44Z`
Commit: `56b00c6bfae18322a847b52275e983945dda2466`
Branch: `redteam/e2e-agent-echo-verification-audit`

## Executive Summary

- Total checks: **398**
- Passed: **297**
- Failed: **91**
- Real critical findings: **0**
- Real high findings: **1**
- Real medium findings: **49**
- Real low findings: **3**
- Expected negative fixture hits: **26**

## Core Invariants

- ✅ `issue_not_archived_echo`: pass
- ✅ `gateway_not_attestation`: pass
- ✅ `claim_gate_required`: pass
- ✅ `propagation_not_promotion`: pass
- ✅ `human_solicited_not_independent`: pass

## Phases Run

### api
- Checks: 99, Passed: 65, Failed: 34

### attestation
- Checks: 6, Passed: 1, Failed: 5

### entrypoints
- Checks: 33, Passed: 29, Failed: 4

### gateway
- Checks: 32, Passed: 25, Failed: 7

### issues
- Checks: 92, Passed: 70, Failed: 12

### propagation
- Checks: 55, Passed: 41, Failed: 14

### release
- Checks: 81, Passed: 66, Failed: 15

## Real Findings

### HIGH

- **Echo ≠ Amendment boundary unclear**
  - File: `api/echo-acceptance-policy.json`
  - Echo acceptance policy must clarify that Echoes are not amendments

### MEDIUM

- **Missing boundary declaration: non_amending**
  - File: `api/agent-entry-protocol.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/agent-required-reading.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/agent-required-reading.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: bitcoin_originals**
  - File: `api/agent-required-reading.json`
  - Agent-facing API should contain 'bitcoin_originals' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/agent-submission-guide.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/submission-checklist.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/submission-checklist.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: bitcoin_originals**
  - File: `api/submission-checklist.json`
  - Agent-facing API should contain 'bitcoin_originals' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/issue-submission-policy.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/issue-submission-policy.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/echo-acceptance-policy.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/echo-acceptance-policy.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: bitcoin_originals**
  - File: `api/echo-acceptance-policy.json`
  - Agent-facing API should contain 'bitcoin_originals' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/propagation-policy.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/propagation-policy.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: bitcoin_originals**
  - File: `api/propagation-policy.json`
  - Agent-facing API should contain 'bitcoin_originals' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/agent-issue-gateway-payload-schema.v1.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/claim-gate-rules.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/claim-gate-rules.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Empty does_not_prove**
  - File: `api/claim-gate-rules.json`
  - n/a
- **Missing boundary declaration: not_authority**
  - File: `api/claim-gate-entrypoint-policy.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/claim-gate-entrypoint-policy.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: bitcoin_originals**
  - File: `api/claim-gate-entrypoint-policy.json`
  - Agent-facing API should contain 'bitcoin_originals' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/verification-levels.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/component-verification-levels.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/echo-types.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/evidence-input-schema.v1.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/evidence-input-schema.v1.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Missing boundary declaration: not_authority**
  - File: `api/claim-gate-output-schema.v1.json`
  - Agent-facing API should contain 'not_authority' boundary declaration
- **Missing boundary declaration: non_amending**
  - File: `api/claim-gate-output-schema.v1.json`
  - Agent-facing API should contain 'non_amending' boundary declaration
- **Entrypoint missing keyword: 'boundary'**
  - File: `/agent-first-contact.md`
  - Expected keyword 'boundary' not found in /agent-first-contact
- **Entrypoint missing keyword: 'not religion'**
  - File: `/agent-brief.md`
  - Expected keyword 'not religion' not found in /agent-brief
- **Entrypoint missing keyword: 'not amendment'**
  - File: `/agent-echo.md`
  - Expected keyword 'not amendment' not found in /agent-echo
- **Entrypoint JSON missing guidance: /api/agent-required-reading.json**
  - File: `/api/agent-required-reading.json`
  - Expected recommended_sequence, context_depth, or required_reading
- **assets_total mismatch: archive/hash-manifest.json**
  - File: `archive/hash-manifest.json`
  - n/a
  - Expected: assets_total = 0
  - Actual: assets_total = -1
- **Manifest note missing boundary: archive/hash-manifest.json**
  - File: `archive/hash-manifest.json`
  - n/a
- **assets_total mismatch: api/evidence-manifest.json**
  - File: `api/evidence-manifest.json`
  - n/a
  - Expected: assets_total = 0
  - Actual: assets_total = -1
- **assets_total mismatch: evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
  - Expected: assets_total = 10
  - Actual: assets_total = -1
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Asset missing non-amending boundary in evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a
- **Manifest note missing boundary: evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json**
  - File: `evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json`
  - n/a

### LOW

- **Missing 'schema' field**
  - File: `api/agent-issue-gateway-payload-schema.v1.json`
  - n/a
- **Missing 'schema' field**
  - File: `api/evidence-input-schema.v1.json`
  - n/a
- **Missing 'schema' field**
  - File: `api/claim-gate-output-schema.v1.json`
  - n/a

## Expected Negative Fixture Hits

The following fixtures are **designed** to trigger detections. Their flags confirm the audit harness is working correctly:

- [CRITICAL] `tests/fixtures/redteam/attestation/custody_notice_claims_physical_verification.json`: Attestation boundary violation: custody_notice_claims_physical_verification.json
- [CRITICAL] `tests/fixtures/redteam/attestation/gateway_claims_attestation.json`: Attestation boundary violation: gateway_claims_attestation.json
- [CRITICAL] `tests/fixtures/redteam/attestation/human_solicited_claims_independent.json`: Attestation boundary violation: human_solicited_claims_independent.json
- [CRITICAL] `tests/fixtures/redteam/attestation/nft_owner_claims_governance.json`: Attestation boundary violation: nft_owner_claims_governance.json
- [CRITICAL] `tests/fixtures/redteam/attestation/test_record_claims_accepted.json`: Attestation boundary violation: test_record_claims_accepted.json
- [MEDIUM] `tests/fixtures/redteam/gateway_payloads/body_too_short.json`: Body length out of bounds: body_too_short.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/claims_gateway_is_attestation.json`: Missing/false boundary: not_attestation in claims_gateway_is_attestation.json
- [CRITICAL] `tests/fixtures/redteam/gateway_payloads/contains_secret_like_token.json`: Secret-like pattern in body: contains_secret_like_token.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: not_authority in missing_boundary_ack.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: not_amendment in missing_boundary_ack.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: not_attestation in missing_boundary_ack.json
- [HIGH] `tests/fixtures/redteam/gateway_payloads/missing_boundary_ack.json`: Missing/false boundary: bitcoin_originals_prevail in missing_boundary_ack.json
- [HIGH] `tests/fixtures/redteam/issue_bodies/fake_v5_freeform_no_claim_gate.md`: Issue fixture flagged: fake_v5_freeform_no_claim_gate.md
- [HIGH] `tests/fixtures/redteam/issue_bodies/gateway_claims_attestation.md`: Issue fixture flagged: gateway_claims_attestation.md
- [HIGH] `tests/fixtures/redteam/issue_bodies/propagation_marketing_overclaim.md`: Issue fixture flagged: propagation_marketing_overclaim.md
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

## Test Results

```
Ran 30 tests in 0.004s — OK
```

## Follow-up Issues

1. `api/echo-acceptance-policy.json` should explicitly state `Echo ≠ Amendment`.
2. Some agent-facing APIs don't individually repeat all boundary keywords.
3. `evidence-images-manifest.json` assets should consider per-asset `non_amending` fields.

