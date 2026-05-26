#!/usr/bin/env python3
"""Gateway public API config must expose expected service endpoint contracts."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "api" / "agent-submit-gateway.json"

data = json.loads(path.read_text(encoding="utf-8"))
text = json.dumps(data)

required_fragments = [
    "/gateway/preflight",
    "/agent-submit",
]

ok = True

for frag in required_fragments:
    if frag not in text:
        print(f"FAIL: agent-submit-gateway missing endpoint fragment: {frag}")
        ok = False

if "/healthz" not in text and "/readiness" not in text:
    print("FAIL: agent-submit-gateway should expose health/readiness endpoint")
    ok = False

if "trinity-agent-issue-gateway.onrender.com" not in text:
    print("FAIL: agent-submit-gateway missing expected Render Gateway host")
    ok = False

if not ok:
    sys.exit(1)

print("PASS: Gateway endpoint contracts exposed")
