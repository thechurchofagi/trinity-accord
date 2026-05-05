#!/usr/bin/env python3
"""
PA-007: Test that echo.yml template provenance/agency enums match
api/evidence-input-schema.v1.json enums.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

schema_path = ROOT / "api" / "evidence-input-schema.v1.json"
template_path = ROOT / ".github" / "ISSUE_TEMPLATE" / "echo.yml"

schema = json.loads(schema_path.read_text(encoding="utf-8"))
template = template_path.read_text(encoding="utf-8")

errors = []

# Extract schema enums
schema_independence = set(
    schema["properties"]["provenance"]["properties"]["independence_class"]["enum"]
)
schema_agency = set(
    schema["properties"]["provenance"]["properties"]["agency_level"]["enum"]
)
schema_operator = set(
    schema["properties"]["verification_session"]["properties"]["operator_type"]["enum"]
)

# Check that every schema enum value appears in the template
for v in sorted(schema_independence):
    if v not in template:
        errors.append(f"echo.yml missing independence_class option: {v}")

for v in sorted(schema_agency):
    if v not in template:
        errors.append(f"echo.yml missing agency_level option: {v}")

for v in sorted(schema_operator):
    if v not in template:
        errors.append(f"echo.yml missing operator_type option: {v}")

# Check required field IDs exist in template
required_ids = [
    "solicited_status",
    "independence_class",
    "agency_level",
    "operator_type",
    "provenance_notes",
]

for rid in required_ids:
    if f"id: {rid}" not in template:
        errors.append(f"echo.yml missing required field id: {rid}")

if errors:
    print("ECHO_TEMPLATE_PROVENANCE_SCHEMA_CONSISTENCY_FAIL")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("ECHO_TEMPLATE_PROVENANCE_SCHEMA_CONSISTENCY_OK")
