#!/usr/bin/env python3
"""Test that invalid V4 Echo records are not indexed as accepted.

RF-003: No flawed historical Echo may be counted as verification.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
errors = []

SCAN_DIRS = [
    ROOT / "echoes",
    ROOT / "verification-reports",
    ROOT / "api",
]

BAD_PHRASES = [
    '"expected": "from api/hashes.json"',
    '"computed": "via downloads/verify.py"',
    "passes 100/100 cases",
    "54 pass, 46 fail",
]


def is_json(path):
    return path.suffix.lower() == ".json"


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ""


for base in SCAN_DIRS:
    if not base.exists():
        continue

    for path in base.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in (".json", ".md", ".txt"):
            continue

        text = read_text(path)
        lower = text.lower()

        mentions_bad_openclaw = (
            "openclaw" in lower
            or "v4-verification-echo-2026-05-03" in lower
        )

        if mentions_bad_openclaw:
            if is_json(path):
                try:
                    obj = json.loads(text)
                except Exception:
                    obj = {}

                status = obj.get("archive_status", "")
                verification_status = obj.get("verification_status", "")
                do_not_count = obj.get("do_not_count_as_attestation", False)

                if status not in ("superseded", "invalidated", "test_record", "legacy_record"):
                    errors.append(f"{path}: OpenClaw May 3 record must be superseded/invalidated")

                if verification_status not in ("invalidated", "superseded", ""):
                    errors.append(f"{path}: unexpected verification_status={verification_status}")

                if status in ("superseded", "invalidated") and do_not_count is not True:
                    errors.append(f"{path}: superseded/invalidated record must set do_not_count_as_attestation=true")

            else:
                if "superseded" not in lower and "invalidated" not in lower:
                    errors.append(f"{path}: OpenClaw May 3 markdown/text record lacks superseded/invalidated marker")

        # Placeholder hash phrases must not appear in accepted records.
        for phrase in BAD_PHRASES:
            if phrase in lower:
                if not any(marker in lower for marker in ["superseded", "invalidated", "historical", "do_not_count"]):
                    errors.append(f"{path}: bad phrase appears outside invalidated/superseded context: {phrase}")

if errors:
    print("INVALID_V4_ECHO_INDEX_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("INVALID_V4_ECHO_INDEX_OK")
