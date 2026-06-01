#!/usr/bin/env python3
"""gateway_v0_v5_policy.parse_bool must not convert malformed strings to false."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from gateway_v0_v5_policy import parse_bool, is_valid_gateway_receipt_block

for value in ["true", "True", "1", "yes", " YES "]:
    if parse_bool(value) is not True:
        print(f"FAIL: expected true for {value!r}")
        sys.exit(1)

for value in ["false", "False", "0", "no", " NO "]:
    if parse_bool(value) is not False:
        print(f"FAIL: expected false for {value!r}")
        sys.exit(1)

for value in ["maybe", "tru", "", "none"]:
    if parse_bool(value) is not None:
        print(f"FAIL: malformed bool should return None: {value!r}")
        sys.exit(1)

bad_receipt = {
    "created_by_gateway": "tru",
    "render_api_only": "true",
    "server_validated": "true",
    "server_rendered": "true",
    "gateway_service": "trinity-agent-issue-gateway",
    "gateway_receipt_id": "gar-20260524T000000Z-fixture",
}

if is_valid_gateway_receipt_block(bad_receipt):
    print("FAIL: malformed gateway bool accepted as valid receipt")
    sys.exit(1)

print("PASS: gateway_v0_v5_policy boolean parsing is strict enough")
