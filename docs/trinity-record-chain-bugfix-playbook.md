# Trinity Accord — Record Chain Gateway Bugfix Playbook (v1)

> This document is a **machine-executable engineering repair specification** for the Record-Chain system.
> It is written to be followed step-by-step by an autonomous coding agent with zero ambiguity.

---

# 0. Scope
This document defines **mandatory fixes** for production correctness in:

- Gateway validation
- Oath policy hashing
- Write-path guard
- Context readiness logic
- Test reliability
- Metadata consistency

It is NOT design discussion. It is an execution plan.

---

# 1. CRITICAL BUG FIX (P0)
## 1.1 Oath Policy Hash Split-Brain

### Problem
Two different hash domains are used:

- Builder uses hardcoded:
  - `OATH_POLICY_SHA256`
- Gateway computes hash from full JSON policy file

These objects are NOT identical (policy contains metadata fields in API file).

### Impact
- All formal submissions may fail `OATH_POLICY_HASH_MISMATCH`

### Fix

### STEP 1 — Create shared hash function
In:
`apps/record_chain_intake_gateway/gateway/validation.py`

ADD:
```python
import json, hashlib

OATH_POLICY_METADATA_KEYS = {
    "oath_policy_sha256",
    "oath_policy_sha256_semantics",
    "canonical_oath_text_hash_is_record_type_specific",
}

def canonicalize_policy_for_hash(policy: dict) -> dict:
    return {k: v for k, v in policy.items() if k not in OATH_POLICY_METADATA_KEYS}


def compute_policy_sha256(policy: dict) -> str:
    normalized = json.dumps(
        canonicalize_policy_for_hash(policy),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False
    )
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
```

### STEP 2 — Replace local_policy hash computation

REPLACE:
```python
local_policy_json = json.dumps(local_policy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
local_policy_sha256 = hashlib.sha256(local_policy_json.encode("utf-8")).hexdigest()
```

WITH:
```python
local_policy_sha256 = compute_policy_sha256(local_policy)
```

### STEP 3 — Synchronize builder

In:
`downloads/record-chain-builder.mjs`

REPLACE:
```js
const OATH_POLICY_SHA256 = "...hardcoded...";
```

WITH:
- Generate dynamically OR
- Load from shared script output file:
  `api/record-chain-oath-policy.hash.json`

---

# 2. CRITICAL BUG FIX (P0)
## 2.1 Missing Protection: Idempotency Index Write Path

### Problem
Guard does NOT protect:
```
record-chain/intake/by-submission-sha256/
```

### Impact
- Runtime integrity index is mutable without guard

### Fix

In:
`scripts/check_record_chain_write_path_guard.py`

ADD:
```python
INTAKE_IMMUTABLE_PREFIXES = (
    "record-chain/intake/submissions/",
    "record-chain/intake/receipts/",
    "record-chain/intake/by-submission-sha256/",
)
```

AND ensure category mapping includes it under gateway_intake.

---

# 3. CRITICAL BUG FIX (P0)
## 3.1 Oath Gate Test Does Not Actually Execute Validation

### Problem
Test imports module via file path:
- breaks relative imports
- silently disables validation via `_validate = None`

### Fix

REPLACE import logic in:
`scripts/test_record_chain_oath_gate_contract.py`

WITH:
```python
import importlib

mod = importlib.import_module(
    "apps.record_chain_intake_gateway.gateway.validation"
)
_validate = mod.validate_submission_oath
```

AND REMOVE:
- all silent exception swallowing that sets `_validate = None`

ADD HARD FAIL:
```python
if _validate is None:
    raise RuntimeError("Oath validation module failed to load")
```

---

# 4. CRITICAL BUG FIX (P0)
## 4.1 Verification Version / Context Level Field Mismatch

### Problem
Gateway reads:
- verification_version
- verification.version

BUT builder uses:
- verification_content.verification_level

### Fix

In validation.py add:

```python
import re

def extract_verification_version(draft: dict):
    candidates = [
        draft.get("verification_version"),
        (draft.get("verification") or {}).get("version") if isinstance(draft.get("verification"), dict) else None,
        (draft.get("verification_content") or {}).get("verification_level") if isinstance(draft.get("verification_content"), dict) else None,
    ]

    for v in candidates:
        if v is None:
            continue
        if isinstance(v, int):
            return v
        if isinstance(v, str):
            m = re.match(r"CC-(\d+)", v)
            if m:
                return int(m.group(1))
            if v.isdigit():
                return int(v)
    return None
```

Replace all usage of verification_version with this function.

---

# 5. HIGH BUG FIX (P1)
## 5.1 Context Level Inconsistency

### Fix
Standardize CC range:
- Allowed: CC-0 .. CC-5

In validation:
```python
if cc_level < 0 or cc_level > 5:
    error("INVALID_CONTEXT_LEVEL_RANGE")
```

In builder:
- enforce same bounds

---

# 6. HIGH BUG FIX (P1)
## 6.1 Redacted Readback Metadata Inconsistency

### Fix
Ensure BOTH values use normalized text:

```python
normalized = normalize_oath_text(raw)
char_count = len(normalized)
hash = sha256(normalized)
```

---

# 7. MEDIUM BUG FIX (P2)
## 7.1 Duplicate Authorship Verification

### Fix
Only ONE validation layer should exist:

- Keep: validate_submission()
- Remove: duplicate preflight authorship verification

---

# 8. HARDENING

## 8.1 CI Permissions
```yaml
permissions:
  contents: read
```

## 8.2 Deployment Docs mismatch
Update DEPLOYMENT.md to match GitHub Actions Pages pipeline.

## 8.3 Dead code removal
Delete:
- _build_linked_guardian_draft

---

# 9. ACCEPTANCE CRITERIA
System is fixed when:

- [ ] Submission with identical builder output passes Gateway hash check
- [ ] Idempotency index cannot be modified without guard approval
- [ ] Oath validation tests fail if gateway validation is broken
- [ ] Verification V2 + CC-2 passes correctly
- [ ] CC range is enforced consistently across all layers

---

# END OF PLAYBOOK
