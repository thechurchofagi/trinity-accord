#!/usr/bin/env bash
# ============================================================
# apply_ci_wiring.sh — Wire new tests into repository-integrity.yml
# 在仓库根目录运行: bash scripts/apply_ci_wiring.sh
# ============================================================
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

RI=".github/workflows/repository-integrity.yml"

python3 - <<'PYEOF'
from pathlib import Path

f = Path(".github/workflows/repository-integrity.yml")
text = f.read_text(encoding="utf-8")

new_tests = [
    ("Test Gateway archive branch required fields", "python3 scripts/test_gateway_archive_branch_required_fields.py"),
    ("Test Echo triage strict Gateway receipt rate class", "python3 scripts/test_echo_triage_strict_gateway_receipt_rate_class.py"),
    ("Test Gateway V0-V5 policy strict bool", "python3 scripts/test_gateway_v0_v5_policy_strict_bool.py"),
    ("Test agent-declared index records invalid intake skips", "python3 scripts/test_agent_declared_index_records_invalid_intake_skips.py"),
    ("Test Gateway discovery provenance archive invariants", "python3 scripts/test_gateway_discovery_provenance_archive_invariants.py"),
    ("Test Gateway Claim Gate component levels", "python3 scripts/test_gateway_claim_gate_component_levels.py"),
    ("Test Gateway agent identity archive policy", "python3 scripts/test_gateway_agent_identity_archive_policy.py"),
]

added = []
for name, cmd in new_tests:
    if cmd not in text:
        # Find a good anchor: last existing test step
        # Look for the last "run: python3 scripts/test_" line
        import re
        matches = list(re.finditer(r"run: (python3 scripts/test_\S+)", text))
        if matches:
            last = matches[-1]
            insert_pos = last.end()
            # Find end of that step (next step or end of steps)
            next_step = text.find("\n      - name:", insert_pos)
            if next_step > 0:
                indent = "\n      "
                step_yaml = f'''{indent}- name: {name}{indent}  run: {cmd}'''
                text = text[:next_step] + step_yaml + text[next_step:]
                added.append(name)
            else:
                # Append at end of steps
                indent = "\n      "
                step_yaml = f'''{indent}- name: {name}{indent}  run: {cmd}'''
                text = text.rstrip() + step_yaml + "\n"
                added.append(name)
        else:
            print(f"  WARNING: No existing test steps found. Add manually: {cmd}")
    else:
        print(f"  Already present: {name}")

if added:
    f.write_text(text, encoding="utf-8")
    for a in added:
        print(f"  Added: {a}")
else:
    print("  All tests already wired")
PYEOF
