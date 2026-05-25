#!/usr/bin/env python3
"""agent-declared index must declare semantic override input."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
index = json.loads((ROOT / "api/agent-declared-verification-index.json").read_text(encoding="utf-8"))

generated_from = set(index.get("generated_from", []))

required = {
    "github_issues:closed",
    "/api/agent-issue-gateway-payload-schema.v1.json",
    "/api/agent-declared-archive-overrides.json",
    "scripts/gateway_v0_v5_policy.py",
}

missing = sorted(required - generated_from)
if missing:
    print(f"FAIL: agent-declared index generated_from missing inputs: {missing}")
    sys.exit(1)

if "override_count" not in index or "overrides_applied" not in index:
    print("FAIL: agent-declared index missing override_count/overrides_applied metadata")
    sys.exit(1)

print("PASS: agent-declared index declares override inputs and metadata")
