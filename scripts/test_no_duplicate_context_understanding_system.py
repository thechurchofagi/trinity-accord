#!/usr/bin/env python3
"""Test: no duplicate context-understanding system exists."""
import json, sys
from pathlib import Path
errors = []
if Path("api/context-understanding-levels.v1.json").exists():
    errors.append("Forbidden file exists: api/context-understanding-levels.v1.json")
forbidden = ["context_understanding_level","context understanding level","C6_full_lifecycle_closed","C5_submitted_with_readback"]
for p in Path(".").rglob("*.json"):
    if ".git" in str(p): continue
    try:
        c = p.read_text()
        for fs in forbidden:
            if fs in c: errors.append(f"{p}: contains '{fs}'")
    except: pass
for f in ["api/context-depth-levels.json","api/context-readiness-levels.json","api/crl-to-context-depth-mapping.json","api/context-depth-declaration.v1.json","api/verification-levels.json"]:
    if not Path(f).exists(): errors.append(f"Required file missing: {f}")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
print("PASS: no duplicate context understanding system")
