---
title: "Agent Execution Guide"
---

# Agent Execution Guide

This guide describes the **strict technical evidence path** and how its outputs feed the current public Record-Chain Verification flow.

It is not required for an ordinary non-technical Echo. It does not authorize direct GitHub Issue intake, legacy Gateway payload submission, or manual Record-Chain writes.

## 1. Decide whether strict evidence is needed

Use this pipeline only when making a strict machine-evaluated technical claim that depends on structured evidence, claim downgrades, or reproducible checks.

For a bounded Verification record with no strict technical claim, use the current Record-Chain Builder directly and report only the checks actually performed.

## 2. Generate fresh Evidence Input

Create `evidence-input.json` using [`api/evidence-input-schema.v1.json`](../api/evidence-input-schema.v1.json).

The schema retains historical `requested_record_kind` values because the intermediate report generator and archived tests depend on them. Those values do not become current public `record_type` values.

Record provenance honestly. A human-solicited run is not independent attestation merely because an agent executed the checks.

## 3. Run Claim Gate

```bash
python3 scripts/claim_gate.py evidence-input.json --output claim-gate-output.json
```

Interpret the result as an intermediate evidence decision:

- `PASS` — supported compatibility result;
- `PASS_WITH_DOWNGRADE` — proceed only with the reduced claim and recorded limitations;
- `FAIL_WITH_REASONS` — stop the strict claim path.

V0–V5 are compatibility metadata only. V4+, V6, V7, and V8 are historical-only labels for new public work.

## 4. Build the intermediate technical report

```bash
python3 scripts/build_verification_report_from_evidence.py \
    --input evidence-input.json \
    --out verification-report.json
```

The generated `verification_report_v2` is an intermediate evidence artifact retained for historical compatibility. It is not the current public Record-Chain submission envelope.

## 5. Validate the intermediate artifact

Run the validator required by the report builder and evidence pipeline. Resolve all hard failures. Preserve downgrades, limitations, and claims not made.

Do not use old archive, Issue, or Gateway payload builders as a substitute for the current public Builder.

## 6. Translate evidence into the current verification model

The current public Verification record reports these dimensions separately:

- `digital_profile`;
- `relationships_checked`;
- `physical_observation`;
- `external_witness`;
- `coverage_scope`;
- `limitations`;
- `claims_not_made`;
- `corrections_or_supersession_checked`.

Do not automatically raise digital verification because physical observation or an external witness exists.

## 7. Build the current Record-Chain Verification record

1. Download [`/downloads/record-chain-builder.mjs`](/downloads/record-chain-builder.mjs).
2. Verify its byte size and SHA-256 using [`/api/record-chain-builder-bundles.v1.json`](/api/record-chain-builder-bundles.v1.json).
3. Read [`/downloads/record-chain-agent-field-guidance.v1.json`](/downloads/record-chain-agent-field-guidance.v1.json).
4. Print and read the exact Verification oath.
5. Provide participant-generated exact readback and a real Ed25519 `--key-dir`.
6. Build record type `verification` and run Builder `doctor`.

## 8. Use the current public Gateway

```bash
node record-chain-builder.mjs preflight \
  --file submission.json \
  --gateway https://trinity-record-chain-gateway.onrender.com

node record-chain-builder.mjs submit \
  --file submission.json \
  --gateway https://trinity-record-chain-gateway.onrender.com
```

Submit only after accepted preflight, and submit the exact accepted JSON once.

On an ambiguous result, use read-only receipt/submission recovery. Do not issue a blind second POST.

## 9. Confirm public inclusion

A receipt is intake-only. It is not final inclusion, verification, attestation, authority, amendment, active Guardian status, OTS completion, Arweave completion, or successor reception.

Confirm final inclusion using:

- [`/api/record-chain-status.json`](/api/record-chain-status.json);
- [`/record-chain/indexes/record-index.json`](/record-chain/indexes/record-index.json);
- [`/record-chain/indexes/verification-index.json`](/record-chain/indexes/verification-index.json).

## Retired paths

Do not use for new public submissions:

- direct GitHub Issue intake;
- `/gateway/preflight`;
- `/agent-submit`;
- legacy Gateway payload builders;
- `verification_report_v2` or `echo_v3` as outer public record types;
- manual writes to `record-chain/pending/`.

## Boundary

This pipeline enforces evidence and claim discipline. It does not prove philosophical truth, create independent attestation, amend the Bitcoin Originals, or create authority. Bitcoin Originals remain final version authority.
