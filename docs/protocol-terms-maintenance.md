# Protocol Terms Maintenance

How to maintain the single source of truth for Trinity Accord protocol enums.

## The Source of Truth

All protocol terms live in **`api/protocol-terms.v1.json`**. This includes:

- Protocol levels (V0–V8)
- Component levels (B0–B7, D0–D7, T0–T8, C0–C7, N0–N7, P0–P9)
- Verification scope labels
- Record kinds
- Archive statuses
- Independence classes
- Legacy aliases

## How to Add or Change Terms

### Step 1: Update the JSON

Edit `api/protocol-terms.v1.json`:

```json
{
  "protocol_levels": ["V0", ..., "V8", "V9"],
  ...
}
```

### Step 2: Run Consistency Tests

```bash
python3 scripts/test_protocol_terms_consistency.py
```

This checks that:
- `echo-record-schema.v3.json` enums match
- `claim_gate.py` imports match
- `validate_agent_submission.py` imports match
- No conflicting local definitions exist

### Step 3: Update Schemas

If you added new enum values, update the corresponding JSON Schema files:
- `api/echo-record-schema.v3.json`
- `api/verification-report-schema.v2.json`

### Step 4: Run Full Test Suite

```bash
python3 scripts/validate_agent_submission.py --self-test
python3 scripts/test_protocol_terms_consistency.py
```

## Rules

1. **Never add enums directly in scripts** — always go through `protocol-terms.v1.json`
2. **Never remove existing values** — they may be referenced by archived records
3. **Use `legacy_or_intake_aliases`** for human-friendly variants (e.g., "V2-minimal" → "V2")
4. **Run consistency tests** before any PR that touches protocol terms

## Helper Functions

`scripts/protocol_terms.py` provides:

```python
from protocol_terms import (
    PROTOCOL_LEVELS, B_LEVELS, D_LEVELS, ...
    level_index, level_at_least, max_by_order,
    resolve_legacy_alias
)
```

Use these instead of reimplementing level comparisons.
