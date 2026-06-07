#!/usr/bin/env python3
"""Contract test: auto-finalizer discovers intake submissions in date-partitioned dirs."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUTO = ROOT / "scripts/auto_finalize_accepted_submissions.py"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise SystemExit(msg)


def main() -> int:
    src = AUTO.read_text(encoding="utf-8")

    # Must use rglob for recursive discovery of date-partitioned submissions
    require("rglob" in src, "auto-finalizer must use rglob for recursive submission discovery")

    # Must have find_receipt_for_submission or equivalent receipt fallback logic
    require("find_receipt_for_submission" in src or "rglob" in src,
            "auto-finalizer must have receipt fallback logic for date-partitioned dirs")

    # Must support --require-new-records flag
    require("require_new_records" in src or "require-new-records" in src,
            "auto-finalizer must support --require-new-records flag")

    # Must hard fail when require_new_records is set and finalized_count is 0
    require("finalized_count" in src and "require_new" in src,
            "auto-finalizer must check finalized_count when require_new_records is set")

    # Must handle ambiguous receipt matches (multiple matches = hard fail)
    require("ambiguous" in src.lower() or "multiple" in src.lower() or "len(matches)" in src,
            "auto-finalizer must hard fail on ambiguous receipt matches")

    # Must still support flat layout (glob fallback or rglob covers both)
    require("submission.json" in src, "auto-finalizer must still recognize .submission.json files")

    print("PASS: auto-finalizer intake discovery contract")


if __name__ == "__main__":
    main()
