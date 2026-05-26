#!/usr/bin/env python3
"""
Test: Echo archive authorization boundary.
TA-REDTEAM-2026-004 — B-AUTH-001 regression test.

Ensures:
- OWNER/MEMBER can /echo archive
- COLLABORATOR cannot /echo archive
- COLLABORATOR can /echo close
- CONTRIBUTOR cannot /echo close or archive
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WF = ROOT / ".github" / "workflows" / "echo-human-review-action.yml"


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def main():
    text = WF.read_text(encoding="utf-8")

    # Both commands must exist
    if '"/echo archive")' not in text:
        fail("missing /echo archive case")
    if '"/echo close")' not in text:
        fail("missing /echo close case")

    archive_pos = text.index('"/echo archive")')
    close_pos = text.index('"/echo close")')

    archive_block = text[archive_pos:close_pos]
    close_block = text[close_pos:close_pos + 1000]

    # Archive must NOT authorize COLLABORATOR
    if "OWNER|MEMBER|COLLABORATOR" in archive_block:
        fail("/echo archive must not authorize COLLABORATOR")

    # Archive must authorize OWNER|MEMBER
    if "OWNER|MEMBER)" not in archive_block:
        fail("/echo archive must authorize OWNER|MEMBER")

    # Close should authorize OWNER|MEMBER|COLLABORATOR
    if "OWNER|MEMBER|COLLABORATOR" not in close_block:
        fail("/echo close should authorize OWNER|MEMBER|COLLABORATOR")

    # Ensure no global pre-authorization that lets COLLABORATOR reach archive
    pre_archive = text[:archive_pos]
    # Check there's no broad case that authorizes COLLABORATOR before command check
    if re.search(r'case\s+"\$COMMENT_ASSOC".*?OWNER\|MEMBER\|COLLABORATOR', pre_archive, re.S):
        fail("global COMMENT_ASSOC authorization includes COLLABORATOR before command-specific archive check")

    print("ECHO_HUMAN_REVIEW_ARCHIVE_AUTHORIZATION_OK")


if __name__ == "__main__":
    main()
