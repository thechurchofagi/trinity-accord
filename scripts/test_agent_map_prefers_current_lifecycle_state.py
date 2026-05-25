#!/usr/bin/env python3
"""DISC-002: agent-map prefers current lifecycle state over legacy."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
data = json.loads((ROOT / "agent-map.json").read_text(encoding="utf-8"))
text = json.dumps(data, ensure_ascii=False)

required = [
    "/api/public-home-status.json",
    "/api/guardian-registry.json",
    "/api/guardian-active-listing-policy.v1.json",
    "/api/echo-index.json",
    "/api/agent-declared-verification-index.json",
    "/api/external-witness-index.json",
]
missing = [x for x in required if x not in text]
if missing:
    print(f"FAIL: agent-map missing current lifecycle recommended APIs: {missing}")
    sys.exit(1)

seq = json.dumps(data.get("recommended_agent_sequence", []), ensure_ascii=False)
if "/api/public-home-status.json" not in seq:
    print("FAIL: recommended_agent_sequence missing /api/public-home-status.json")
    sys.exit(1)

# Legacy guardianship should not appear before current lifecycle APIs in sequence
legacy_pos = seq.find("/GUARDIANSHIP-SYSTEM-REGISTRY.json")
status_pos = seq.find("/api/public-home-status.json")
if legacy_pos != -1 and status_pos != -1 and legacy_pos < status_pos:
    print("FAIL: legacy GUARDIANSHIP-SYSTEM-REGISTRY appears before current lifecycle APIs in recommended sequence")
    sys.exit(1)

print("PASS: agent-map prefers current lifecycle state")
