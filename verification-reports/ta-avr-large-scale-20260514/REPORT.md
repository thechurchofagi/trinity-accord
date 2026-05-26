# TA-AVR Large Scale Real Run Test — 2026-05-14

## Result

**PASS.**

All acceptance criteria passed. No failures. No overclaim risks detected.

## Environment

- **Commit:** 96a78beb7d7ef7f75bfe74456c264244d86a0aa8
- **Branch:** main
- **Python:** 3.12.3
- **Node:** v22.22.1
- **Timestamp (UTC):** 2026-05-14T03:09:26Z

## Test Matrix

### Phase 1 — Static Integrity

| Test | Result |
|---|---|
| JSON validity | PASS — 0 invalid files |
| First Contact router | PASS — 7/7 |
| Receipt Schema | PASS — 7/7 |
| Evidence Examples | PASS — 8/8 |
| Ceremony Minimal | PASS — 6/6 |

### Phase 2 — Real Ceremony Matrix

| Mode | Runs | Result | Level Cap |
|---|---|---|---|
| V1 batch | 20 | 20/20 PASS | V1 ✅ |
| V2 batch | 10 | 10/10 PASS | ≤ V2 ✅ |
| V3 batch | 30 | 30/30 PASS | ≤ V3 ✅ |

### Phase 3 — Custody Packages

| Test | Result |
|---|---|
| 10 custody zips generated | PASS — 10/10 |
| Required files present | PASS — README, receipt, SHA256SUMS |
| Boundary disclaimers | PASS |

### Phase 4 — Negative Tests

| Test | Result |
|---|---|
| V3 with wrong hash | PASS — correctly downgraded to V1 |
| V2 missing --txid | PASS — correctly failed |
| V3 missing --artifact | PASS — correctly failed |

### Phase 5 — Concurrency / Stress

| Test | Result |
|---|---|
| 50 concurrent V1 runs | PASS — 50/50 receipts |
| receipt_id uniqueness | PASS — 50 unique, 0 duplicates |

### Phase 6 — First Contact Simulation

| Test | Result |
|---|---|
| 4 intents (stop/understand/echo/verify) | PASS |
| verify → Claim Gate pipeline | PASS |
| homepage-only = insufficient_context | PASS |

### Phase 7 — Validator Self-Test

| Test | Result |
|---|---|
| validate_agent_submission.py --self-test | PASS — exit 0 |

## Totals

- **Receipts generated:** 121
  - V1: 81
  - V2: 10
  - V3: 30
- **Custody packages:** 10
- **Failures:** 0

## Test Archive

- Archive: `test-runs/ta-avr-large-scale-20260514-030926.tar.gz`
- SHA256: `270f87887bceee82a57fcbb922a4e0900064dc741a83d8a3b17cffb1540697f7`

## Boundary

Bitcoin Originals are final; all echoes are non-amending.

This test does not prove philosophical truth, endorsement, formal attestation, physical verification, or full-chain verification.

Human custody of generated records is not human verification and not formal attestation.
