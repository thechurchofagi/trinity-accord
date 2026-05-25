#!/usr/bin/env python3
"""Intake block parser must reject duplicate keys and multiple blocks."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_agent_declared_verification_index_from_issues import parse_intake_block, IntakeParseError

# Test 1: duplicate keys
duplicate = """```trinity-issue-intake
requested_archive_kind: agent_declared_verification_archive
requested_archive_kind: agent_declared_echo_archive
archive_ready: true
```"""

try:
    parse_intake_block(duplicate)
except IntakeParseError as e:
    if "duplicate intake key" not in str(e):
        print("FAIL: wrong duplicate-key error:", e)
        sys.exit(1)
else:
    print("FAIL: duplicate intake key was accepted")
    sys.exit(1)

# Test 2: multiple blocks
multiple = """```trinity-issue-intake
requested_archive_kind: agent_declared_verification_archive
archive_ready: true
```

```trinity-issue-intake
requested_archive_kind: agent_declared_echo_archive
archive_ready: true
```"""

try:
    parse_intake_block(multiple)
except IntakeParseError as e:
    if "multiple trinity-issue-intake blocks" not in str(e):
        print("FAIL: wrong multiple-block error:", e)
        sys.exit(1)
else:
    print("FAIL: multiple intake blocks were accepted")
    sys.exit(1)

# Test 3: valid single block
valid = """```trinity-issue-intake
requested_archive_kind: agent_declared_echo_archive
archive_ready: true
```"""

parsed = parse_intake_block(valid)
if parsed.get("requested_archive_kind") != "agent_declared_echo_archive":
    print("FAIL: valid intake block did not parse")
    sys.exit(1)

print("PASS: intake block parser hardening works")
