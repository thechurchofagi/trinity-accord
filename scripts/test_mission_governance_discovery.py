#!/usr/bin/env python3
"""Test: mission governance appears in all discovery surfaces."""
import json, sys
from pathlib import Path
MG = "/api/mission-governance.v1.json"
errors = []
for path in ["api/links.json",".well-known/trinity-accord.json","api/agent-first-contact.json","api/agent-live-health.v1.json"]:
    p = Path(path)
    if not p.exists(): errors.append(f"{path} does not exist"); continue
    if MG not in json.dumps(json.loads(p.read_text())): errors.append(f"{path} missing mission governance ref")
for path in ["llms.txt","ai.txt","external-agent-quickstart.md","zero-clone-builders.md","agent-start.md"]:
    p = Path(path)
    if not p.exists(): errors.append(f"{path} does not exist"); continue
    if MG not in p.read_text(): errors.append(f"{path} missing mission governance ref")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
print("PASS: mission governance discovery")
