#!/usr/bin/env python3
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "scripts" / "run_ci_group.py"
text = path.read_text(encoding="utf-8")
old = '''        ["python3", "scripts/test_record_chain_verifier_invariants.py"],
        ["python3", "scripts/test_deep_integrity_group_nonempty.py"],'''
new = '''        ["python3", "scripts/test_record_chain_verifier_invariants.py"],
        ["python3", "scripts/test_classification_update_final_binding.py"],
        ["python3", "scripts/test_deep_integrity_group_nonempty.py"],'''
if text.count(old) != 1:
    raise SystemExit("expected exactly one p0 registry insertion point")
path.write_text(text.replace(old, new), encoding="utf-8")
print("Registered classification final-binding regression.")
