#!/usr/bin/env python3
from pathlib import Path
import json
ROOT = Path(__file__).resolve().parents[1]
PAIRS = [
    ("api/record-chain-submission-schema.v1.json", "apps/record_chain_intake_gateway/schemas/record_chain_submission.schema.json"),
    ("api/record-chain-preflight-response.v1.json", "apps/record_chain_intake_gateway/schemas/preflight_response.schema.json"),
    ("api/record-chain-submit-response.v1.json", "apps/record_chain_intake_gateway/schemas/submit_response.schema.json"),
    ("api/record-chain-server-receipt.v1.json", "apps/record_chain_intake_gateway/schemas/server_receipt.schema.json"),
]
for public, shadow in PAIRS:
    a = json.loads((ROOT / public).read_text(encoding="utf-8"))
    b = json.loads((ROOT / shadow).read_text(encoding="utf-8"))
    if a != b:
        raise AssertionError(f"Gateway shadow schema drift: {shadow} != {public}")
print("PASS: Gateway app schemas are exact canonical mirrors")
