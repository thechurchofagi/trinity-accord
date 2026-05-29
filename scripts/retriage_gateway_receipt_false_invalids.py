#!/usr/bin/env python3
"""Backfill false-invalid Gateway-created Issues after receipt triage fix.

Dry-run by default.
Use --apply to mutate labels/state.
"""
from __future__ import annotations

import argparse

REMOVE_LABELS = [
    "echo:invalid",
    "invalid:direct-issue-archive-attempt",
    "not-counted",
    "auto-closed",
    "render-api-required",
]

ADD_LABELS = [
    "agent-gateway-intake",
    "agent-declared",
]

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default="thechurchofagi/trinity-accord")
    parser.add_argument("--issue", type=int, action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    print("Dry-run mode" if not args.apply else "APPLY mode")
    print("Target issues:", args.issue or [299])
    print("TODO: implement using gh CLI or existing GitHub REST helper.")
    print("Safety criteria:")
    print("- author == trinity-accord-agent-issue-gateway[bot]")
    print("- validate_gateway_receipt(...) returns valid")
    print("- issue has invalid:direct-issue-archive-attempt or not-counted")
    print("- issue has Gateway archive decision marker or legacy gateway fields")
    print("Would remove:", REMOVE_LABELS)
    print("Would add/keep:", ADD_LABELS)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
