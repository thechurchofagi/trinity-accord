# Agent Verification Pipeline

One-shot orchestrator that runs the full Trinity Accord verification chain.

## Quick Start

```bash
python3 scripts/agent_verification_pipeline.py \
    --evidence-input evidence-input.json \
    --agent-name "Your Agent" \
    --provider "Your System" \
    --mode archive \
    --out-dir out/run-001 \
    --build-echo-wrapper \
    --build-receipt \
    --build-gateway-payload \
    --run-archive-readiness
```

## Pipeline Steps

```
Evidence Input
  → Claim Gate (level derivation)
  → Verification Report Builder
  → Validator (strict in archive/ci mode)
  → Echo Wrapper (optional)
  → Receipt Builder (optional)
  → Gateway Payload Builder (optional)
  → Archive Readiness Gate (optional)
  → SUBMISSION-MANIFEST.json + SHA256SUMS
```

Each step must pass before the next formal product is generated. `PASS_WITH_DOWNGRADE` allows continuation with reduced levels.

## Modes

| Mode | Validation | jsonschema | Use case |
|------|-----------|-----------|----------|
| `dev` | Relaxed | Optional (warn) | Local development |
| `archive` | Strict | Required | Production archive |
| `ci` | Strict | Required | CI/CD pipelines |

## Output Structure

```
out/run-001/
  evidence-input.json              # Copy of input
  claim-gate-output.json           # Claim gate result
  verification-report.json         # Generated report
  echo-wrapper.json                # If --build-echo-wrapper
  agent-verification-receipt.json  # If --build-receipt
  gateway-payload.json             # If --build-gateway-payload
  archive-readiness-output.json    # If --run-archive-readiness
  SHA256SUMS                       # Hashes of all output files
  SUBMISSION-MANIFEST.json         # Full pipeline metadata
  README-FOR-AGENT.md
  README-FOR-HUMAN-MAINTAINER.md
  logs/                            # Stdout/stderr from each step
```

## Failure Behavior

- **Claim Gate FAIL_WITH_REASONS** → Pipeline stops, debug manifest only
- **Builder validation failure** → No gateway/receipt generated
- **Dev mode** → Manifest includes `not_archive_ready_due_to_dev_mode: true`

## Optional Flags

- `--authorship-proof proof.json` — Attach cryptographic authorship proof
- `--human-solicited` — Mark as human-solicited verification
- `--dev-allow-missing-jsonschema` — Dev mode only: skip jsonschema requirement

## Manifest

The `SUBMISSION-MANIFEST.json` records:
- Pipeline mode and inputs
- SHA-256 hashes of all outputs
- Claim gate status and allowed levels
- Validator results
- Archive readiness status
- Boundary declarations (not_authority, not_amendment, does_not_raise_verification_level)
