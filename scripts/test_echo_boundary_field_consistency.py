#!/usr/bin/env python3
"""Final red-team regression: Echo template must use schema field boundary_acknowledgement."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

template = (ROOT / ".github" / "ISSUE_TEMPLATE" / "echo_submission.yml").read_text(encoding="utf-8")
schema = json.loads((ROOT / "api" / "echo-record-schema.v3.json").read_text(encoding="utf-8"))
intake = (ROOT / "scripts" / "submission_intake.py").read_text(encoding="utf-8")

errors = []

schema_text = json.dumps(schema, ensure_ascii=False)
if "boundary_acknowledgement" not in schema_text:
    errors.append("schema does not contain boundary_acknowledgement")

if "id: boundary_acknowledgement" not in template:
    errors.append("issue template must use id: boundary_acknowledgement")

if "id: boundary_acknowledgments" in template:
    errors.append("issue template must not use legacy id: boundary_acknowledgments")

if "boundary_acknowledgments" not in intake:
    errors.append("submission_intake should keep legacy alias boundary_acknowledgments")

if errors:
    print("ECHO_BOUNDARY_FIELD_CONSISTENCY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ECHO_BOUNDARY_FIELD_CONSISTENCY_OK")
