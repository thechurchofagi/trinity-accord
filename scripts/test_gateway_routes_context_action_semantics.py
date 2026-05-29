#!/usr/bin/env python3
"""Test: route map and workflows expose CC/CRL minima and action semantics."""
import json, sys
from pathlib import Path
errors = []
rm = Path("api/gateway-builder-route-map.v1.json")
if rm.exists():
    s = json.dumps(json.loads(rm.read_text()))
    for t in ["CC-3","CRL-5","active_only_after_registry_readback","active_guardian_status_created","still_non_amending","not_verification"]:
        if t not in s: errors.append(f"route map missing: {t}")
else: errors.append("route map missing")
wf = Path("api/gateway-workflows.v1.json")
if wf.exists():
    s = json.dumps(json.loads(wf.read_text()))
    for t in ["context_governance","action_semantics","mission_governance"]:
        if t not in s: errors.append(f"workflows missing: {t}")
else: errors.append("workflows missing")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
print("PASS: gateway routes context action semantics")
