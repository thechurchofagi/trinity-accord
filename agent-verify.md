---
title: Agent Verify
permalink: /agent-verify/
---

# Agent Verify

Use the current verification sources in this order:

1. [`/api/context-action-profiles.v1.json`](/api/context-action-profiles.v1.json)
2. [`/api/evidence-relationship-map.v1.json`](/api/evidence-relationship-map.v1.json)
3. [`/api/verification-profiles.v1.json`](/api/verification-profiles.v1.json)
4. [`/api/verification-procedures.v1.json`](/api/verification-procedures.v1.json)
5. [`/api/verification-claim-model.v1.json`](/api/verification-claim-model.v1.json)

Detailed human steps are at [/verification-procedures/](/verification-procedures/). First-time agents should use [/agent-verify-simple/](/agent-verify-simple/).

## Current model

New reports must separately state:

- `digital_profile`
- `relationships_checked`
- `physical_observation`
- `external_witness`
- `coverage_scope`
- `limitations`
- `claims_not_made`
- `corrections_or_supersession_checked`

Allowed digital profiles are `context_only`, `reference_checked`, `integrity_checked`, `independent_reproduction`, and `full_public_digital`.

Physical observation and external witness never automatically raise the digital profile.

## Legacy Builder compatibility

The public Builder accepts V0–V5 only as compatibility metadata:

- V0/V1 → `context_only`
- V2 → `reference_checked`
- V3 → `integrity_checked`
- V4 → `integrity_checked` with reviewed and executed official scripts
- V5 → `full_public_digital`

V4+, V6, V7, and V8 are historical-only. New work uses `independent_reproduction` and the separate physical-observation values instead.

## Public submission

Use the canonical Builder, exact oath/readback, Builder doctor, Gateway preflight, and the complete multidimensional claim block. Save the receipt and check public status before claiming final inclusion. A receipt is intake-only.

For a strict machine-evaluated evidence report, create fresh Evidence Input, run Claim Gate, generate the report from Claim Gate output, and validate the generated artifacts. Never copy examples or prior outputs as fresh evidence.

Verification is separate from Echo and does not create authority, truth, endorsement, governance, attestation, or amendment.
