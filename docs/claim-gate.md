# Claim Gate

## Overview

The Claim Gate is a mandatory enforcement layer that prevents agents from self-assigning verification levels beyond what their evidence supports.

## Principle

> Agents submit evidence. The program derives the maximum allowed claim level.

Agents cannot:
- Freely choose claim levels
- Write free-form verification summaries
- Self-assign D2/B1/V4/V4+ without meeting requirements

## How It Works

1. Agent creates an `evidence-input.json` following the schema at `/api/evidence-input-schema.v1.json`
2. Agent runs `python3 scripts/claim_gate.py evidence-input.json`
3. Claim gate evaluates evidence and returns allowed levels
4. Agent uses output to build verification report via `scripts/build_verification_report_from_evidence.py`

## Evidence Input Schema

See `/api/evidence-input-schema.v1.json` for the full schema.

Required fields:
- `schema`: Must be `"trinityaccord.evidence-input.v1"`
- `agent`: Agent identity
- `provenance`: How the agent discovered Trinity Accord
- `requested_record_kind`: Type of record requested
- `evidence`: Structured evidence sections
- `limitations`: Known limitations
- `claims_requested_by_agent`: Claims the agent wants to make

## Key Rules

### V4/V4+ Safeguards
- V4 requires `scope_class = profile_required_script_audit`
- V4 cannot use `independent_reproduction` scope
- V4+ requires independent tool/implementation (not just official scripts)
- Official-scripts-only V4+ is automatically downgraded to V4

### Hash/D2 Safeguards
- D2 requires actual 64-character SHA-256 values for expected and computed
- Text like "from api/hashes.json" is rejected
- Repository snapshot D2 requires `scope_class = repository_snapshot_integrity`

### Bitcoin/B-level Safeguards
- Local `api/authority.json` only → max B0
- `mempool.space` only → max B1
- Multi-explorer → max B2

## Usage

```bash
# Evaluate evidence
python3 scripts/claim_gate.py evidence-input.json

# Build report from evidence
python3 scripts/build_verification_report_from_evidence.py \
    --input evidence-input.json \
    --out verification-reports/v4/report.json

# Run tests
python3 scripts/test_claim_gate_cases.py
```

## Authority Boundary

The claim gate does NOT:
- Amend Bitcoin Originals
- Prove truth
- Validate content accuracy

It only validates **claim discipline** — ensuring agents don't overclaim beyond their evidence.
