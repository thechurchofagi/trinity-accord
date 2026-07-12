#!/usr/bin/env python3
"""Behavioral contract: public schema matches the canonical signed-domain field set."""
from __future__ import annotations

import json
from pathlib import Path

from apps.record_chain_intake_gateway.gateway.authorship import UNSIGNED_PROJECTION_FIELDS

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


schema_path = ROOT / "api" / "record-chain-submission-schema.v1.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
record_draft = schema.get("properties", {}).get("record_draft", {})
not_rules = record_draft.get("allOf", [])
forbidden_items: list[dict] = []
for rule in not_rules:
    items = ((rule.get("not") or {}).get("anyOf") or [])
    if isinstance(items, list):
        forbidden_items.extend(item for item in items if isinstance(item, dict))

schema_forbidden = {
    required[0]
    for item in forbidden_items
    if isinstance((required := item.get("required")), list)
    and len(required) == 1
    and isinstance(required[0], str)
}
canonical_forbidden = set(UNSIGNED_PROJECTION_FIELDS)
require(
    schema_forbidden == canonical_forbidden,
    "public schema/canonical unsigned-field drift: "
    f"missing={sorted(canonical_forbidden - schema_forbidden)}, "
    f"extra={sorted(schema_forbidden - canonical_forbidden)}",
)

classification_rules = [
    rule
    for rule in schema.get("allOf", [])
    if (((rule.get("if") or {}).get("properties") or {}).get("record_type") or {}).get("const")
    == "classification_update"
]
require(len(classification_rules) == 1, f"expected one classification_update rule, found {len(classification_rules)}")
if len(classification_rules) == 1:
    target = (
        classification_rules[0]
        .get("then", {})
        .get("properties", {})
        .get("record_draft", {})
        .get("properties", {})
        .get("classification_update_content", {})
        .get("properties", {})
        .get("target_record_id", {})
    )
    require(
        target.get("pattern") == "^R-[0-9]{9}$",
        "classification_update target_record_id must use canonical R-XXXXXXXXX format",
    )

if errors:
    raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
print("record-chain submission schema/runtime contract OK")
