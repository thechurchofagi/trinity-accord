#!/usr/bin/env python3
"""Semantic validator must not contain unreachable validation code after CLI entrypoint."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "validate_gateway_payload_semantics.py"
src = path.read_text(encoding="utf-8")
tree = ast.parse(src)

validate_func = next(
    (n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "validate"),
    None,
)
if validate_func is None:
    print("FAIL: validate() function not found")
    sys.exit(1)

validate_src = ast.get_source_segment(src, validate_func) or ""

required_fragments = [
    "evidence_requirement_mode",
    "discovery_provenance",
    "allowed_component_levels",
    "self_reported",
    "authorship_proof",
]

ok = True
for frag in required_fragments:
    if frag not in validate_src:
        print(f"FAIL: validate() missing required semantic check fragment: {frag}")
        ok = False

bad_tail_fragments = [
    "# BRANCH-REQ-001/002",
    "# DISCOVERY-001",
    "# CLAIM-COMP-001",
    "# IDENTITY-001",
]

entry = 'if __name__ == "__main__":'
if entry in src:
    tail = src.split(entry, 1)[1]
    for frag in bad_tail_fragments:
        if frag in tail:
            print(f"FAIL: validation code appears after CLI entrypoint: {frag}")
            ok = False

if not ok:
    sys.exit(1)

print("PASS: semantic validator has no unreachable validation code")
