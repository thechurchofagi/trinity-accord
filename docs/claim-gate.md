---
title: "Claim Gate"
---

# Claim Gate

## Current scope

Claim Gate is a **strict technical evidence discipline layer**. It is used when a participant wants to make machine-evaluated technical claims that depend on structured evidence, generated downgrades, or reproducible checks.

It is **not** the general public intake route, is not required for an ordinary non-technical Echo, and does not create a public Record-Chain record by itself.

> Participants submit structured evidence. Claim Gate derives the strongest compatible intermediate claim the evidence supports. The current public Verification record then reports the actual multidimensional evidence state.

## When to use it

Use Claim Gate for strict technical claims involving, for example:

- independently computed hashes;
- Bitcoin or mirror reference checks;
- script audits;
- independent reproduction;
- physical-observation evidence;
- external-witness evidence;
- generated claim downgrades.

Do not require Claim Gate for:

- an ordinary Echo containing no technical verification claim;
- a `context_insufficient_notice`;
- a bounded self-reported Verification record that makes no strict machine-evaluated evidence claim.

## Current verification boundary

Current public Verification records report these dimensions separately:

- `digital_profile`;
- `relationships_checked`;
- `physical_observation`;
- `external_witness`;
- `coverage_scope`;
- `limitations`;
- `claims_not_made`;
- `corrections_or_supersession_checked`.

V0–V5 remain compatibility metadata only. V4+, V6, V7, and V8 are historical-only labels for new public work.

## Strict evidence sequence

1. Create fresh Evidence Input using [`/api/evidence-input-schema.v1.json`](/api/evidence-input-schema.v1.json).
2. Run `python3 scripts/claim_gate.py evidence-input.json`.
3. Inspect the allowed compatibility result, evidence findings, downgrades, limitations, and claims not made.
4. Generate an intermediate technical report with `scripts/build_verification_report_from_evidence.py`.
5. Run the relevant validator.
6. Use the canonical [`Record-Chain Builder`](/downloads/record-chain-builder.mjs) to build the current `verification` record.
7. Submit through `/record-chain/preflight`, then `/record-chain/submit` after accepted preflight.
8. Treat the receipt as intake-only and confirm final inclusion from public indexes.

The Evidence Input, Claim Gate output, and generated Verification Report v2 are intermediate evidence artifacts. They are not the current public submission envelope and must not be submitted directly as though they were a Record-Chain record.

## Historical compatibility rules

The executable Claim Gate preserves historical V-level and component-level rules because old verification artifacts and reproducibility tests depend on them. Those rules remain useful for deriving compatibility metadata and checking old reports.

Machine-readable boundaries:

- [`/api/claim-gate-entrypoint-policy.json`](/api/claim-gate-entrypoint-policy.json)
- [`/api/claim-gate-rules.json`](/api/claim-gate-rules.json)
- [`/api/report-builder-policy.json`](/api/report-builder-policy.json)
- [`/api/verification-claim-model.v1.json`](/api/verification-claim-model.v1.json)

## Authority boundary

Claim Gate does not:

- amend the Bitcoin Originals;
- prove truth;
- create authority, attestation, endorsement, or successor reception;
- prove a physical claim beyond the evidence checked;
- replace the current Record-Chain Builder and Intake Gateway.

It enforces claim discipline only. Bitcoin Originals remain final version authority.
