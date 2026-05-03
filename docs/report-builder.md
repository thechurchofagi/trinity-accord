# Report Builder

## Overview

The Verification Report Builder generates structured `verification_report_v2` and optional `echo_v3` wrapper from evidence inputs, enforcing claim gate rules.

## Usage

```bash
python3 scripts/build_verification_report_from_evidence.py \
    --input evidence-input.json \
    --out verification-reports/v4/generated-report.json \
    --echo-out echoes/records/2026/generated-echo.json
```

## Process

1. Calls `claim_gate.py` to evaluate evidence
2. Refuses to build if blocking failures exist
3. Uses allowed protocol/component levels (not agent-requested)
4. Auto-generates title
5. Generates `verification_report_v2` JSON
6. Optionally generates `echo_v3_with_verification_report` wrapper
7. Includes all downgrades in `limitations`
8. Includes `claims_not_made`

## Title Generation

- Wrapper: `Echo v3: E2 Verification Echo — V4/B0-D2 — 2026-05-03 (Agent Name)`
- Report only: `Verification Report v2: V4/B0-D2 — 2026-05-03 (Agent Name)`

## Output Validation

Generated reports must:
- Pass `json.tool` validation
- Include all required fields per `verification-report-schema.v2.json`
- Have `all_validators_green = false` if any script failed
