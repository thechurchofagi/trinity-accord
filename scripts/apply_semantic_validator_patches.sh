#!/usr/bin/env bash
# ============================================================
# apply_semantic_validator_patches.sh
# 在仓库根目录运行: bash scripts/apply_semantic_validator_patches.sh
# ============================================================
set -euo pipefail

echo "WARNING: This script is a best-effort patch helper, not a verification tool."
echo "Run repository-integrity and behavior tests before treating changes as complete."
cd "$(git rev-parse --show-toplevel)"

SV="scripts/validate_gateway_payload_semantics.py"

python3 - <<'PYEOF'
from pathlib import Path

f = Path("scripts/validate_gateway_payload_semantics.py")
text = f.read_text(encoding="utf-8")

patches_applied = []

# --- PART A §6: evidence_requirement_mode checks ---
erm_block = '''    if kind in {"agent_declared_echo_archive", "guardian_active_registry_listing_request"}:
        if payload.get("evidence_requirement_mode") != "not_applicable_for_echo":
            errors.append(
                f"{kind} requires evidence_requirement_mode=not_applicable_for_echo"
            )

    if kind == "agent_declared_verification_archive":
        if payload.get("evidence_requirement_mode") != "waived_for_v0_v5":
            errors.append(
                "agent_declared_verification_archive requires evidence_requirement_mode=waived_for_v0_v5"
            )
'''

if "evidence_requirement_mode" not in text or "requires evidence_requirement_mode" not in text:
    # Find a good insertion point: after kind extraction or first if kind block
    # Look for the pattern where archive kind checks happen
    inserted = False
    for anchor in [
        'if kind in {"agent_declared_echo_archive"',
        'if kind == "agent_declared_verification_archive"',
        "archive_kind",
    ]:
        if anchor in text:
            # Insert before the first archive kind check
            idx = text.index(anchor)
            # Find the start of that line
            line_start = text.rfind("\n", 0, idx) + 1
            text = text[:line_start] + erm_block + "\n" + text[line_start:]
            inserted = True
            patches_applied.append("§6 evidence_requirement_mode checks")
            break
    if not inserted:
        print("  WARNING: Could not auto-insert evidence_requirement_mode checks. Add manually.")
else:
    print("  §6 evidence_requirement_mode checks already present")

# --- PART E §11: discovery_provenance checks ---
dp_block = '''        discovery = payload.get("discovery_provenance")
        if not isinstance(discovery, dict):
            errors.append("discovery_provenance must be a non-null object")
        elif not str(discovery.get("source", "")).strip():
            errors.append("discovery_provenance.source must be a non-empty string")
'''

if "discovery_provenance must be a non-null object" not in text:
    # Insert after evidence_requirement_mode block
    if "evidence_requirement_mode" in text:
        idx = text.index("evidence_requirement_mode")
        # Find end of that block (next blank line or next if)
        next_section = text.find("\n\n", idx)
        if next_section > 0:
            text = text[:next_section+2] + dp_block + text[next_section+2:]
            patches_applied.append("§11 discovery_provenance checks")
    else:
        print("  WARNING: Could not auto-insert discovery_provenance checks. Add manually.")
else:
    print("  §11 discovery_provenance checks already present")

# --- PART F §12: claim_gate allowed_component_levels checks ---
cg_block = '''            components = claim_gate.get("allowed_component_levels")
            if components is not None:
                if not isinstance(components, dict):
                    errors.append("claim_gate.allowed_component_levels must be an object when present")
                else:
                    allowed_component_keys = {
                        "context_depth",
                        "evidence_depth",
                        "tool_reproduction",
                        "independence",
                    }
                    unknown = sorted(set(components) - allowed_component_keys)
                    if unknown:
                        errors.append(
                            f"claim_gate.allowed_component_levels contains unknown keys: {unknown}"
                        )
'''

if "allowed_component_levels" not in text:
    # Insert after claim_gate checks
    if "claim_gate" in text:
        idx = text.index("claim_gate")
        # Find the end of claim_gate block
        next_section = text.find("\n\n", idx)
        if next_section > 0:
            text = text[:next_section+2] + cg_block + text[next_section+2:]
            patches_applied.append("§12 claim_gate component levels checks")
    else:
        print("  WARNING: Could not auto-insert claim_gate component levels checks. Add manually.")
else:
    print("  §12 claim_gate component levels checks already present")

# --- PART G §13: agent_identity.self_reported policy ---
id_block = '''    if kind in {
        "agent_declared_verification_archive",
        "agent_declared_echo_archive",
        "guardian_active_registry_listing_request",
    }:
        identity = payload.get("agent_identity") or {}
        if identity.get("self_reported") is not True:
            level = identity.get("identity_verification_level")
            if level not in {"signed_statement", "institutional_domain", "notarial_identity"}:
                errors.append(
                    "agent_identity.self_reported=false requires signed_statement, institutional_domain, or notarial_identity"
                )
            if not payload.get("authorship_proof"):
                errors.append(
                    "agent_identity.self_reported=false requires authorship_proof"
                )
'''

if "self_reported=false requires signed_statement" not in text:
    # Insert at end of validate function, before return
    if "return errors" in text:
        text = text.replace("return errors", id_block + "\n    return errors")
        patches_applied.append("§13 agent_identity.self_reported policy")
    elif "return " in text:
        # Find last return
        idx = text.rfind("return ")
        line_start = text.rfind("\n", 0, idx) + 1
        text = text[:line_start] + id_block + "\n" + text[line_start:]
        patches_applied.append("§13 agent_identity.self_reported policy")
    else:
        print("  WARNING: Could not auto-insert self_reported policy. Add manually.")
else:
    print("  §13 agent_identity.self_reported policy already present")

f.write_text(text, encoding="utf-8")

for p in patches_applied:
    print(f"  Applied: {p}")
if not patches_applied:
    print("  No patches needed or all already present")
PYEOF
