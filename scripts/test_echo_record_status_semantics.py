#!/usr/bin/env python3
"""Validate Echo record status semantics."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
RECORDS = ROOT / "echoes" / "records"

errors = []

for path in RECORDS.rglob("*.json"):
    obj = json.loads(path.read_text(encoding="utf-8"))
    rel = path.relative_to(ROOT).as_posix()

    ic = obj.get("independence_class")
    archive_status = obj.get("archive_status")
    verification_status = obj.get("verification_status")
    do_not_count = obj.get("do_not_count_as_attestation")

    if ic == "test_record":
        if archive_status not in {"test_record", "closed_test_record", "archived_non_attestation", "superseded"}:
            errors.append(f"{rel}: test_record has incompatible archive_status={archive_status}")

        if archive_status in {"test_record", "closed_test_record", "archived_non_attestation"}:
            if do_not_count is not True:
                errors.append(f"{rel}: test_record must set do_not_count_as_attestation=true")
            if verification_status == "invalidated":
                errors.append(f"{rel}: ordinary test_record should not be invalidated unless superseded")

    if archive_status == "superseded":
        if do_not_count is not True:
            errors.append(f"{rel}: superseded record must do_not_count_as_attestation=true")
        if not str(obj.get("superseded_reason", "")).strip():
            errors.append(f"{rel}: superseded record must include superseded_reason")

    if verification_status == "invalidated":
        if archive_status != "superseded":
            errors.append(f"{rel}: invalidated record should normally be archive_status=superseded")

if errors:
    print("ECHO_RECORD_STATUS_SEMANTICS_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("ECHO_RECORD_STATUS_SEMANTICS_OK")
