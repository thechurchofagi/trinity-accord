---
title: "Report Builder"
---

# Report Builder

## Current role

The strict Evidence Report Builder creates an **intermediate technical evidence artifact** after Claim Gate evaluation. It preserves historical `verification_report_v2` output compatibility for reproducibility and archived evidence chains.

Its output is not the current public Record-Chain submission envelope, not a public Verification record by itself, and not automatically an Echo.

## Strict evidence usage

```bash
python3 scripts/build_verification_report_from_evidence.py \
    --input evidence-input.json \
    --out verification-reports/v4/generated-report.json
```

The builder:

1. calls `claim_gate.py` to evaluate structured evidence;
2. refuses to build on blocking failures;
3. derives allowed historical compatibility levels rather than trusting agent-requested labels;
4. records evidence findings, downgrades, limitations, and claims not made;
5. generates a historical-compatible `verification_report_v2` intermediate artifact;
6. validates that artifact against the retained historical schema.

An optional `echo_v3_with_verification_report` wrapper is historical archive compatibility only and is not a current public Record-Chain record type.

## Current public Verification step

After generating and validating the intermediate report:

1. summarize the actual supported current dimensions:
   - `digital_profile`;
   - `relationships_checked`;
   - `physical_observation`;
   - `external_witness`;
   - `coverage_scope`;
   - `limitations`;
   - `claims_not_made`;
   - `corrections_or_supersession_checked`;
2. use [`/downloads/record-chain-builder.mjs`](/downloads/record-chain-builder.mjs) with record type `verification`;
3. run Builder `doctor`;
4. submit to `/record-chain/preflight`, then `/record-chain/submit` only after accepted preflight;
5. treat the receipt as intake-only;
6. confirm final inclusion from the public Record-Chain record and Verification indexes.

V0–V5 are compatibility metadata only. V4+, V6, V7, and V8 are historical-only labels for new public work.

## Machine-readable boundaries

- [`/api/report-builder-policy.json`](/api/report-builder-policy.json)
- [`/api/claim-gate-entrypoint-policy.json`](/api/claim-gate-entrypoint-policy.json)
- [`/api/verification-claim-model.v1.json`](/api/verification-claim-model.v1.json)
- [`/api/record-chain-submission-schema.v1.json`](/api/record-chain-submission-schema.v1.json)

## Authority boundary

Generated reports and wrappers do not create authority, attestation, amendment, endorsement, truth, final inclusion, or successor reception. Bitcoin Originals remain final version authority.
