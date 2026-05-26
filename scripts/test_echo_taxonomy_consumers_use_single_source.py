#!/usr/bin/env python3
"""Archive and validator must consume Echo taxonomy from protocol_echo_types.py."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

archive = (ROOT / "scripts/archive_echo_issue.py").read_text(encoding="utf-8")
validator = (ROOT / "scripts/validate_agent_submission.py").read_text(encoding="utf-8")

if "echo_type_map_for_archive" not in archive:
    print("FAIL: archive_echo_issue.py does not use echo_type_map_for_archive")
    sys.exit(1)

if "ECHO_TYPE_MAP = {" in archive:
    print("FAIL: archive_echo_issue.py still hardcodes ECHO_TYPE_MAP")
    sys.exit(1)

if "allowed_canonical_echo_types" not in validator:
    print("FAIL: validate_agent_submission.py does not use allowed_canonical_echo_types")
    sys.exit(1)

if "CANONICAL_ECHO_TYPES = {" in validator:
    print("FAIL: validate_agent_submission.py still hardcodes CANONICAL_ECHO_TYPES")
    sys.exit(1)

print("PASS: Echo taxonomy consumers use single source loader")
