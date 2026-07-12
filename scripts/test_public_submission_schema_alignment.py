#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from apps.record_chain_intake_gateway.gateway.authorship import UNSIGNED_PROJECTION_FIELDS

schema = json.loads((ROOT / "api" / "record-chain-submission-schema.v1.json").read_text(encoding="utf-8"))
record_draft = schema["properties"]["record_draft"]
forbidden_items = record_draft["allOf"][0]["not"]["anyOf"]
forbidden = {
    item["required"][0]
    for item in forbidden_items
    if isinstance(item.get("required"), list) and len(item["required"]) == 1
}
if forbidden != set(UNSIGNED_PROJECTION_FIELDS):
    missing = sorted(set(UNSIGNED_PROJECTION_FIELDS) - forbidden)
    extra = sorted(forbidden - set(UNSIGNED_PROJECTION_FIELDS))
    raise SystemExit(f"public submission schema unsigned-field drift: missing={missing}, extra={extra}")

classification_rules = [
    rule for rule in schema["allOf"]
    if (((rule.get("if") or {}).get("properties") or {}).get("record_type") or {}).get("const") == "classification_update"
]
if len(classification_rules) != 1:
    raise SystemExit(f"expected one classification_update schema rule, found {len(classification_rules)}")
target = classification_rules[0]["then"]["properties"]["record_draft"]["properties"]["classification_update_content"]["properties"]["target_record_id"]
if target.get("pattern") != "^R-[0-9]{9}$":
    raise SystemExit("classification_update target_record_id schema must require canonical R-XXXXXXXXX format")
print("PASS: public submission schema matches Gateway signed-domain and target-id contracts")
