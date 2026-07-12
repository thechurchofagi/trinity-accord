#!/usr/bin/env python3
"""Behavioral contract: public schema matches the canonical signed-domain field set."""
from __future__ import annotations

import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def require(condition: bool, message: str) -> None:
    if not condition:
        errors.append(message)


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
            raise SystemExit("UNSIGNED_PROJECTION_FIELDS must remain a literal frozenset for contract extraction")
        fields = {
            element.value
            for element in value.args[0].elts
            if isinstance(element, ast.Constant) and isinstance(element.value, str)
        }
        if len(fields) != len(value.args[0].elts):
            raise SystemExit("UNSIGNED_PROJECTION_FIELDS must contain only string literals")
        return fields
    raise SystemExit("UNSIGNED_PROJECTION_FIELDS assignment not found")


schema_path = ROOT / "api" / "record-chain-submission-schema.v1.json"
schema = json.loads(schema_path.read_text(encoding="utf-8"))
record_draft = schema.get("properties", {}).get("record_draft", {})
forbidden_items: list[dict] = []
for rule in record_draft.get("allOf", []):
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
canonical_forbidden = canonical_unsigned_fields()
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
    require(target.get("pattern") == "^R-[0-9]{9}$", "classification_update target_record_id must use canonical R-XXXXXXXXX format")

if errors:
    raise SystemExit("\n".join(f"ERROR: {error}" for error in errors))
print("record-chain submission schema/runtime contract OK")
