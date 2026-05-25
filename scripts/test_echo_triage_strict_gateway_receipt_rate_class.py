#!/usr/bin/env python3
"""echo-triage rate classifier must use strict Gateway receipt fields."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
workflow = (ROOT / ".github/workflows/echo-triage.yml").read_text(encoding="utf-8")

required_fragments = [
    'hasMachineFlag(body, "created_by_gateway", "true")',
    'hasMachineFlag(body, "render_api_only", "true")',
    'hasMachineFlag(body, "server_validated", "true")',
    'hasMachineFlag(body, "server_rendered", "true")',
    'service === "trinity-agent-issue-gateway"',
    'gateway_receipt_id',
    'gar-',
]

ok = True
for frag in required_fragments:
    if frag not in workflow:
        print(f"FAIL: echo-triage.yml strict receipt classifier missing: {frag}")
        ok = False

m = re.search(r"function\s+isGatewayCreated\s*\([^)]*\)\s*\{(?P<body>.*?)\}", workflow, re.S)
if not m:
    print("FAIL: could not find isGatewayCreated function in echo-triage.yml")
    sys.exit(1)

body = m.group("body")
for frag in ["render_api_only", "server_rendered", "gateway_service", "gateway_receipt_id"]:
    if frag not in body:
        print(f"FAIL: isGatewayCreated remains too loose; missing {frag}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: echo-triage Gateway rate classifier uses strict receipt fields")
