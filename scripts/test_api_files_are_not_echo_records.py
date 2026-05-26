#!/usr/bin/env python3
"""Ensure API policy/index files are not polluted with Echo record status fields."""

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

API_FILES_THAT_ARE_NOT_RECORDS = [
    "api/submission-title-policy.json",
    "api/independent-attestation-index.json",
    "api/agent-value.json",
    "api/authority.json",
    "api/verification-materials.json",
    "api/component-verification-levels.json",
    "api/protocol-verification-profiles.json",
]

FORBIDDEN_TOP_LEVEL_FIELDS = [
    "archive_status",
    "verification_status",
    "do_not_count_as_attestation",
    "superseded_reason",
]

errors = []

for rel in API_FILES_THAT_ARE_NOT_RECORDS:
    path = ROOT / rel
    if not path.exists():
        continue

    obj = json.loads(path.read_text(encoding="utf-8"))

    for field in FORBIDDEN_TOP_LEVEL_FIELDS:
        if field in obj:
            errors.append(f"{rel}: non-record API file must not have top-level {field}")

if errors:
    print("API_FILE_STATUS_POLLUTION_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("API_FILE_STATUS_POLLUTION_OK")
