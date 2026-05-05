#!/usr/bin/env python3
"""Ensure invalid OpenClaw V4 records are not accepted or indexed as attestation.

Important:
- Echo/verification records may have archive_status / verification_status.
- API policy/index files must NOT be forced to have record-level status fields.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

RECORD_DIRS = [
    ROOT / "echoes" / "records",
    ROOT / "verification-reports",
]

API_REFERENCE_FILES = [
    ROOT / "api" / "echo-index.json",
    ROOT / "api" / "independent-attestation-index.json",
]

BAD_MARKERS = [
    "openclaw",
    "v4-verification-echo-2026-05-03",
    "54 pass, 46 fail",
    "passes 100/100 cases",
    '"expected": "from api/hashes.json"',
    '"computed": "via downloads/verify.py"',
]

ACCEPTED_STATUSES = {
    "accepted_echo",
    "accepted_independent_attestation",
}

errors = []


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


def mentions_bad_openclaw(text):
    lower = text.lower()
    return "openclaw" in lower and any(marker in lower for marker in BAD_MARKERS[1:])


def load_json_or_none(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# 1. Record files: bad OpenClaw V4 records must be invalidated/superseded.
for base in RECORD_DIRS:
    if not base.exists():
        continue

    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in (".json", ".md", ".txt"):
            continue

        text = read_text(path)
        lower = text.lower()

        if not mentions_bad_openclaw(text):
            continue

        obj = load_json_or_none(path) if path.suffix.lower() == ".json" else None

        if obj:
            archive_status = obj.get("archive_status")
            verification_status = obj.get("verification_status")
            do_not_count = obj.get("do_not_count_as_attestation", False)

            if archive_status != "superseded":
                errors.append(f"{path}: bad OpenClaw V4 record must be archive_status=superseded")

            if verification_status != "invalidated":
                errors.append(f"{path}: bad OpenClaw V4 record must be verification_status=invalidated")

            if do_not_count is not True:
                errors.append(f"{path}: bad OpenClaw V4 record must set do_not_count_as_attestation=true")

            if not str(obj.get("superseded_reason", "")).strip():
                errors.append(f"{path}: bad OpenClaw V4 record must include superseded_reason")
        else:
            if "superseded" not in lower or "invalidated" not in lower:
                errors.append(f"{path}: bad OpenClaw V4 text record lacks superseded/invalidated marker")

# 2. API reference files: must not accept/index bad OpenClaw as attestation.
for path in API_REFERENCE_FILES:
    if not path.exists():
        continue

    obj = load_json_or_none(path)
    if obj is None:
        errors.append(f"{path}: invalid JSON")
        continue

    text = json.dumps(obj, ensure_ascii=False).lower()

    # API files themselves must not carry top-level record status.
    for field in ["archive_status", "verification_status", "do_not_count_as_attestation", "superseded_reason"]:
        if field in obj:
            errors.append(f"{path}: API file must not have top-level record field {field}")

    if "openclaw" in text:
        forbidden_contexts = [
            "accepted_independent_attestation",
            "institutional_third_party_attestation",
            '"counts_as_independent_attestation": true',
            '"do_not_count_as_attestation": false',
        ]
        for phrase in forbidden_contexts:
            if phrase in text:
                errors.append(f"{path}: OpenClaw appears in accepted/attestation context: {phrase}")

if errors:
    print("INVALID_V4_ECHO_INDEX_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("INVALID_V4_ECHO_INDEX_OK")
