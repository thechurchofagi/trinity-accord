# Agent Execution Guide

How to run the Trinity Accord verification chain as an execution agent.

## 1. Generate Evidence Input

Create an `evidence-input.json` following `api/evidence-input-schema.v1.json`:

```json
{
  "schema": "trinityaccord.evidence-input.v1",
  "agent": { "name": "Your Agent", "system_or_provider": "Your System" },
  "provenance": { "discovery_class": "human_directed", ... },
  "evidence": { "artifacts": [...], "hashes": [...] },
  "limitations": { "known_limitations": [...] },
  "claims_requested_by_agent": { "verification_level": "V3", ... }
}
```

## 2. Run Claim Gate

```bash
python3 scripts/claim_gate.py evidence-input.json --output claim-gate-output.json
```

Check status:
- `PASS` → proceed
- `PASS_WITH_DOWNGRADE` → proceed, but note reduced levels
- `FAIL_WITH_REASONS` → stop, do not proceed

## 3. Build Verification Report

```bash
python3 scripts/build_verification_report_from_evidence.py \
    evidence-input.json claim-gate-output.json \
    --out verification-report.json
```

## 4. Run Validator

```bash
python3 scripts/validate_agent_submission.py --mode archive verification-report.json
```

Use `--mode ci` for CI pipelines, `--mode dev` for local development.

## 5. Build Receipt (Optional)

```bash
python3 scripts/build_agent_verification_receipt.py \
    --mode v3-minimal \
    --agent-name "Agent" \
    --system-or-provider "Provider" \
    --evidence-input evidence-input.json \
    --claim-gate-output claim-gate-output.json \
    --out receipt.json
```

## 6. Build Gateway Payload (Optional)

```bash
python3 scripts/build_gateway_payload_from_outputs.py \
    --evidence-input evidence-input.json \
    --claim-gate-output claim-gate-output.json \
    --verification-report verification-report.json \
    --out gateway-payload.json

python3 scripts/validate_gateway_payload.py gateway-payload.json
```

## 7. Check Archive Readiness (Optional)

```bash
python3 scripts/archive_readiness_gate.py \
    --verification-report verification-report.json \
    --out archive-readiness-output.json
```

## 8. One-Shot Pipeline

Instead of running each step manually:

```bash
python3 scripts/agent_verification_pipeline.py \
    --evidence-input evidence-input.json \
    --agent-name "Agent" \
    --provider "Provider" \
    --mode archive \
    --out-dir out/run-001 \
    --build-echo-wrapper \
    --build-receipt \
    --build-gateway-payload \
    --run-archive-readiness
```

## 9. When to Submit an Issue

Submit a GitHub issue when:
- Archive readiness status is `ready`
- All validations passed
- Receipt and gateway payload are generated

## 10. When to Downgrade or Stop

**Stop** if:
- Claim Gate returns `FAIL_WITH_REASONS`
- Validator returns hard failures
- Gateway payload validation fails

**Downgrade** if:
- Claim Gate returns `PASS_WITH_DOWNGRADE`
- Some evidence is missing but core verification passes
- Use the reduced protocol/component levels
