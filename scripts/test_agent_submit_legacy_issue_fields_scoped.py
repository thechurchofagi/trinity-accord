#!/usr/bin/env python3
"""
Agent Submit Legacy Issue Fields Scoped Test.
Validates that manual Issue / trinity-issue-intake sections in agent-submit.md
are properly scoped away from V0-V5 agent-declared archive.

Usage:
    python3 scripts/test_agent_submit_legacy_issue_fields_scoped.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PASS_COUNT = 0
FAIL_COUNT = 0
TOTAL = 0


def check(condition, label):
    global PASS_COUNT, FAIL_COUNT, TOTAL
    TOTAL += 1
    if condition:
        PASS_COUNT += 1
        print(f"  PASS: {label}")
    else:
        FAIL_COUNT += 1
        print(f"  FAIL: {label}")


print("=== Agent Submit Legacy Issue Fields Scoped Test ===\n")

content = (ROOT / "agent-submit.md").read_text(encoding="utf-8")

# Check heading exists and is properly scoped
check("Legacy / V6+ Verification Echo Issue fields" in content,
      "agent-submit.md has 'Legacy / V6+ Verification Echo Issue fields' heading")

check("This section does not apply to V0, V1, V2, V3, V4, V4+, or V5" in content,
      "agent-submit.md scopes legacy section away from V0-V5 archive")

# Check that 'explicit GitHub Issue form fields' only appears AFTER the scoping statement
parts = content.split("This section does not apply")
if len(parts) >= 2:
    before_scope = parts[0]
    after_scope = "This section does not apply".join(parts[1:])
    check("explicit GitHub Issue form fields" not in before_scope,
          "'explicit GitHub Issue form fields' does not appear before scope statement")
    check("explicit GitHub Issue form fields" in after_scope,
          "'explicit GitHub Issue form fields' appears after scope statement")
else:
    check(False, "Scope statement found in content")

# Check agents-submit.md top hard rule is present
check("Do not request a GitHub PAT" in content,
      "agent-submit.md top has no-PAT rule")

check("V4+ is a distinct template-mode level" in content or "V4+ is a distinct" in content,
      "agent-submit.md has V4+ distinct level statement")

print(f"\n=== Results: {PASS_COUNT}/{TOTAL} passed ===")
if FAIL_COUNT > 0:
    print(f"FAILED: {FAIL_COUNT} checks failed")
    sys.exit(1)
else:
    print("AGENT_SUBMIT_LEGACY_ISSUE_FIELDS_SCOPED_OK")
    sys.exit(0)
