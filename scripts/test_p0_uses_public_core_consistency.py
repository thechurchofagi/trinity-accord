#!/usr/bin/env python3
"""p0-main should use small public core consistency, not broad legacy consistency."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
tree = ast.parse((ROOT / "scripts" / "run_ci_group.py").read_text(encoding="utf-8"))

groups_node = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "GROUPS":
                groups_node = node.value

groups = ast.literal_eval(groups_node)
p0_cmds = {" ".join(cmd) for cmd in groups["p0-main"]}

if "python3 scripts/check_consistency.py" in p0_cmds:
    print("FAIL: p0-main should not run broad check_consistency.py")
    sys.exit(1)

if "python3 scripts/check_public_core_consistency.py" not in p0_cmds:
    print("FAIL: p0-main must run check_public_core_consistency.py")
    sys.exit(1)

print("PASS: p0-main uses public core consistency")
