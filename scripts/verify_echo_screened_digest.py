#!/usr/bin/env python3
"""
Verify that the current issue body/title match the screened digest from triage.

Usage:
    python3 scripts/verify_echo_screened_digest.py \
        --issue-json issue.json \
        --comments-json comments.json

Exit codes:
    0 = digest matches (issue unchanged since screening)
    1 = mismatch, missing digest, or error
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from echo_issue_digest import (
    compute_issue_screening_digest,
    extract_digest_from_comments,
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Verify Echo screened digest")
    ap.add_argument("--issue-json", required=True, help="Path to issue JSON")
    ap.add_argument("--comments-json", required=True, help="Path to issue comments JSON")
    args = ap.parse_args()

    issue = json.loads(Path(args.issue_json).read_text(encoding="utf-8"))
    comments = json.loads(Path(args.comments_json).read_text(encoding="utf-8"))

    title = issue.get("title") or ""
    body = issue.get("body") or ""

    current_digest = compute_issue_screening_digest(title, body)
    stored_digest = extract_digest_from_comments(comments)

    if stored_digest is None:
        print("ECHO_SCREENED_DIGEST_MISSING", file=sys.stderr)
        print("No screened digest found in triage comments.", file=sys.stderr)
        print(f"current_digest={current_digest}", file=sys.stderr)
        return 1

    if current_digest != stored_digest:
        print("ECHO_SCREENED_DIGEST_MISMATCH", file=sys.stderr)
        print(f"expected={stored_digest}", file=sys.stderr)
        print(f"actual={current_digest}", file=sys.stderr)
        return 1

    print("ECHO_SCREENED_DIGEST_OK")
    print(f"digest={current_digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
