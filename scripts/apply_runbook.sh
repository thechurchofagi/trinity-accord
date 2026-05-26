#!/usr/bin/env bash
# ============================================================
# apply_runbook.sh — 一键执行 trinity_remaining_gateway_risks_hardening_runbook
# 在仓库根目录运行: bash scripts/apply_runbook.sh
# ============================================================
set -euo pipefail

echo "WARNING: This script is a best-effort patch helper, not a verification tool."
echo "Run repository-integrity and behavior tests before treating changes as complete."
cd "$(git rev-parse --show-toplevel)"

echo "=== PART A: Require evidence_requirement_mode in schema branches ==="

SCHEMA="api/agent-issue-gateway-payload-schema.v1.json"

# BRANCH-REQ-001: Add evidence_requirement_mode to agent_declared_echo_archive then.required
python3 - <<'PY'
import json, sys
from pathlib import Path

f = Path("api/agent-issue-gateway-payload-schema.v1.json")
s = json.loads(f.read_text(encoding="utf-8"))

changed = False
# Walk through allOf to find the branch with requested_archive_kind=agent_declared_echo_archive
for item in s.get("allOf", []):
    then = item.get("then", {})
    props = then.get("properties", {})
    rak = props.get("requested_archive_kind", {})
    if rak.get("const") == "agent_declared_echo_archive":
        req = then.get("required", [])
        if "evidence_requirement_mode" not in req:
            req.append("evidence_requirement_mode")
            then["required"] = req
            changed = True
            print("  [BRANCH-REQ-001] Added evidence_requirement_mode to agent_declared_echo_archive required")
            break

if changed:
    f.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
else:
    print("  [BRANCH-REQ-001] Already present or branch not found")
PY

# BRANCH-REQ-002: Add evidence_requirement_mode to guardian_active_registry_listing_request then.required
python3 - <<'PY'
import json, sys
from pathlib import Path

f = Path("api/agent-issue-gateway-payload-schema.v1.json")
s = json.loads(f.read_text(encoding="utf-8"))

changed = False
for item in s.get("allOf", []):
    then = item.get("then", {})
    props = then.get("properties", {})
    rak = props.get("requested_archive_kind", {})
    if rak.get("const") == "guardian_active_registry_listing_request":
        req = then.get("required", [])
        if "evidence_requirement_mode" not in req:
            req.append("evidence_requirement_mode")
            then["required"] = req
            changed = True
            print("  [BRANCH-REQ-002] Added evidence_requirement_mode to guardian listing required")
            break

if changed:
    f.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
else:
    print("  [BRANCH-REQ-002] Already present or branch not found")
PY

echo ""
echo "=== PART E: Require non-null discovery_provenance for archive branches ==="

python3 - <<'PY'
import json
from pathlib import Path

f = Path("api/agent-issue-gateway-payload-schema.v1.json")
s = json.loads(f.read_text(encoding="utf-8"))

dp_override = {
    "type": "object",
    "additionalProperties": True,
    "required": ["source"],
    "properties": {
        "source": {
            "type": "string",
            "minLength": 1,
            "maxLength": 200
        }
    }
}

targets = {
    "agent_declared_verification_archive",
    "agent_declared_echo_archive",
    "guardian_active_registry_listing_request",
}

changed = False
for item in s.get("allOf", []):
    then = item.get("then", {})
    props = then.get("properties", {})
    rak = props.get("requested_archive_kind", {})
    if rak.get("const") in targets:
        if props.get("discovery_provenance", {}).get("type") != "object":
            props["discovery_provenance"] = dp_override
            then["properties"] = props
            changed = True
            print(f"  [DISCOVERY-001] Override discovery_provenance for {rak['const']}")

if changed:
    f.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
else:
    print("  [DISCOVERY-001] All branches already have object discovery_provenance")
PY

echo ""
echo "=== PART F: Constrain claim_gate.allowed_component_levels ==="

python3 - <<'PY'
import json
from pathlib import Path

f = Path("api/agent-issue-gateway-payload-schema.v1.json")
s = json.loads(f.read_text(encoding="utf-8"))

comp_schema = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "context_depth": {"type": "string", "enum": ["D0","D1","D2","D3","D4","D5"]},
        "evidence_depth": {"type": "string", "enum": ["E0","E1","E2","E3","E4","E5"]},
        "tool_reproduction": {"type": "string", "enum": ["T0","T1","T2","T3","T4","T5"]},
        "independence": {"type": "string", "enum": ["I0","I1","I2","I3","I4","I5"]},
    }
}

changed = False
for item in s.get("allOf", []):
    then = item.get("then", {})
    props = then.get("properties", {})
    rak = props.get("requested_archive_kind", {})
    if rak.get("const") == "agent_declared_verification_archive":
        cg = props.get("claim_gate", {})
        cg_props = cg.get("properties", {})
        acl = cg_props.get("allowed_component_levels", {})
        if acl.get("additionalProperties") is not False:
            cg_props["allowed_component_levels"] = comp_schema
            cg["properties"] = cg_props
            props["claim_gate"] = cg
            changed = True
            print("  [CLAIM-COMP-001] Constrained allowed_component_levels")

if changed:
    f.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
else:
    print("  [CLAIM-COMP-001] Already constrained")
PY

echo ""
echo "=== PART C: Strict parse_bool in gateway_v0_v5_policy.py ==="

python3 - <<'PY'
import re
from pathlib import Path

f = Path("scripts/gateway_v0_v5_policy.py")
text = f.read_text(encoding="utf-8")

old = """def parse_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.strip().lower() in ("true", "1", "yes")
    return None"""

new = '''def parse_bool(value):
    """Strictly parse a boolean-like value.

    Returns True / False for known encodings.
    Returns None for missing or malformed values.
    """
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("true", "1", "yes"):
            return True
        if v in ("false", "0", "no"):
            return False
        return None
    return None'''

if old in text:
    text = text.replace(old, new)
    f.write_text(text, encoding="utf-8")
    print("  [RECEIPT-BOOL-001] Replaced parse_bool with strict version")
elif "if v in (\"false\", \"0\", \"no\")" in text:
    print("  [RECEIPT-BOOL-001] Already strict")
else:
    print("  [RECEIPT-BOOL-001] WARNING: Could not find parse_bool to replace — check manually")
PY

echo ""
echo "=== PART D: Record invalid intake skips in index metadata ==="

python3 - <<'PY'
from pathlib import Path

f = Path("scripts/build_agent_declared_verification_index_from_issues.py")
text = f.read_text(encoding="utf-8")

# Add skipped_invalid_intake = [] near other skipped_ lists
if "skipped_invalid_intake" not in text:
    # Find the pattern and add after it
    anchor = "skipped_missing_oath_summary = []"
    if anchor in text:
        text = text.replace(
            anchor,
            anchor + "\n    skipped_invalid_intake = []"
        )
        print("  [INDEX-AUDIT-001] Added skipped_invalid_intake list")
    else:
        print("  [INDEX-AUDIT-001] WARNING: Could not find anchor for skipped_invalid_intake")

    # Replace IntakeParseError handler
    old_intake = 'except IntakeParseError as e:\n        print(f"SKIP_INVALID_INTAKE issue #{issue.get(\'number\')}: {e}", file=sys.stderr)\n        continue'
    new_intake = '''except IntakeParseError as e:
        skipped_invalid_intake.append({
            "issue_number": issue.get("number"),
            "reason": str(e),
        })
        print(f"SKIP_INVALID_INTAKE issue #{issue.get('number')}: {e}", file=sys.stderr)
        continue'''
    if old_intake in text:
        text = text.replace(old_intake, new_intake)
        print("  [INDEX-AUDIT-001] Updated IntakeParseError handler")

    # Replace BoolParseError handler
    old_bool = 'except BoolParseError as e:\n        print(f"SKIP_INVALID_INTAKE issue #{issue.get(\'number\')}: {e}", file=sys.stderr)\n        continue'
    new_bool = '''except BoolParseError as e:
        skipped_invalid_intake.append({
            "issue_number": issue.get("number"),
            "reason": str(e),
        })
        print(f"SKIP_INVALID_INTAKE issue #{issue.get('number')}: {e}", file=sys.stderr)
        continue'''
    if old_bool in text:
        text = text.replace(old_bool, new_bool)
        print("  [INDEX-AUDIT-001] Updated BoolParseError handler")

    # Add to return dict
    anchor2 = '"skipped_missing_oath_summary": skipped_missing_oath_summary,'
    if anchor2 in text:
        text = text.replace(
            anchor2,
            anchor2 + '\n        "skipped_invalid_intake": skipped_invalid_intake,'
        )
        print("  [INDEX-AUDIT-001] Added skipped_invalid_intake to return dict")

    f.write_text(text, encoding="utf-8")
else:
    print("  [INDEX-AUDIT-001] Already present")
PY

echo ""
echo "=== PART B: Strict echo-triage Gateway receipt classifier ==="
echo "  [TRIAGE-RECEIPT-001] Requires manual edit of .github/workflows/echo-triage.yml"
echo "  Replace isGatewayCreated() function with the version from the runbook."
echo "  Skipping — too complex for safe auto-patch. Edit manually."

echo ""
echo "=== PART G: agent_identity.self_reported policy ==="
echo "  [IDENTITY-001] Requires manual edit of scripts/validate_gateway_payload_semantics.py"
echo "  Add the self_reported/archive policy block per runbook. Skipping auto-patch."

echo ""
echo "=== PART A (semantic validator): evidence_requirement_mode defense-in-depth ==="
echo "  Requires manual edit of scripts/validate_gateway_payload_semantics.py"
echo "  Add evidence_requirement_mode checks per runbook §6. Skipping auto-patch."

echo ""
echo "=== PART E (semantic validator): discovery_provenance defense-in-depth ==="
echo "  Requires manual edit of scripts/validate_gateway_payload_semantics.py"
echo "  Add discovery_provenance checks per runbook §11. Skipping auto-patch."

echo ""
echo "=== PART F (semantic validator): claim_gate component levels defense-in-depth ==="
echo "  Requires manual edit of scripts/validate_gateway_payload_semantics.py"
echo "  Add allowed_component_levels checks per runbook §12. Skipping auto-patch."

echo ""
echo "=========================================="
echo "  Auto-patchable parts applied!"
echo "=========================================="
echo ""
echo "Remaining MANUAL edits needed:"
echo "  1. .github/workflows/echo-triage.yml — replace isGatewayCreated() (runbook §8)"
echo "  2. scripts/validate_gateway_payload_semantics.py — add 4 defense-in-depth blocks (§6, §11, §12, §13)"
echo "  3. .github/workflows/repository-integrity.yml — wire 7 new tests (§14)"
echo ""
echo "After manual edits, run validation:"
echo "  python3 -m json.tool api/agent-issue-gateway-payload-schema.v1.json >/dev/null"
echo "  python3 scripts/test_gateway_archive_branch_required_fields.py"
echo "  python3 scripts/test_gateway_v0_v5_policy_strict_bool.py"
echo "  python3 scripts/test_agent_declared_index_records_invalid_intake_skips.py"
echo "  python3 scripts/test_gateway_discovery_provenance_archive_invariants.py"
echo "  python3 scripts/test_gateway_claim_gate_component_levels.py"
echo "  python3 scripts/test_gateway_agent_identity_archive_policy.py"
echo "  python3 scripts/test_echo_triage_strict_gateway_receipt_rate_class.py"
