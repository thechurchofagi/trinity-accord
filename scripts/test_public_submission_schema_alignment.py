#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def canonical_unsigned_fields() -> set[str]:
    path = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "authorship.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(isinstance(target, ast.Name) and target.id == "UNSIGNED_PROJECTION_FIELDS" for target in node.targets):
            continue
        value = node.value
        if not (
            isinstance(value, ast.Call)
            and isinstance(value.func, ast.Name)
            and value.func.id == "frozenset"
            and len(value.args) == 1
            and isinstance(value.args[0], ast.Set)
        ):
            raise SystemExit("UNSIGNED_PROJECTION_FIELDS must remain a literal frozenset")
        fields = {
            element.value
            for element in value.args[0].elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        }
        if len(fields) != len(value.args[0].elts):
            raise SystemExit("UNSIGNED_PROJECTION_FIELDS must contain only string literals")
        return fields
    raise SystemExit("UNSIGNED_PROJECTION_FIELDS assignment not found")


def classification_content(rule: dict) -> dict:
    return (
        rule.get("then", {})
        .get("properties", {})
        .get("record_draft", {})
        .get("properties", {})
        .get("classification_update_content", {})
    )


schema = json.loads((ROOT / "api" / "record-chain-submission-schema.v1.json").read_text(encoding="utf-8"))
record_draft = schema["properties"]["record_draft"]
forbidden_items = record_draft["allOf"][0]["not"]["anyOf"]
forbidden = {
    item["required"][0]
    for item in forbidden_items
    if isinstance(item.get("required"), list) and len(item["required"]) == 1
}
canonical = canonical_unsigned_fields()
if forbidden != canonical:
    missing = sorted(canonical - forbidden)
    extra = sorted(forbidden - canonical)
    raise SystemExit(f"public submission schema unsigned-field drift: missing={missing}, extra={extra}")

classification_rules = [
    rule
    for rule in schema["allOf"]
    if (((rule.get("if") or {}).get("properties") or {}).get("record_type") or {}).get("const") == "classification_update"
    and classification_content(rule)
]
if len(classification_rules) != 1:
    raise SystemExit(f"expected one classification_update content rule, found {len(classification_rules)}")
target = classification_content(classification_rules[0])["properties"]["target_record_id"]
if target.get("pattern") != "^R-[0-9]{9}$":
    raise SystemExit("classification_update target_record_id schema must require canonical R-XXXXXXXXX format")
print("PASS: public submission schema matches Gateway signed-domain and target-id contracts")
