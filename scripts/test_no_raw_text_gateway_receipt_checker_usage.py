#!/usr/bin/env python3
"""Archive/index/workflow paths must not use raw-text Gateway receipt checker."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
forbidden = "has_valid_gateway_receipt_in_text("
allowed = {
    "scripts/gateway_v0_v5_policy.py",
    "scripts/test_no_raw_text_gateway_receipt_checker_usage.py",
}

ok = True
paths = list((ROOT / "scripts").glob("*.py")) + list((ROOT / ".github" / "workflows").glob("*.yml"))
for path in paths:
    rel = path.relative_to(ROOT).as_posix()
    if rel in allowed:
        continue
    if forbidden in path.read_text(encoding="utf-8"):
        print(f"FAIL: raw-text receipt checker used in {rel}")
        ok = False

if not ok:
    sys.exit(1)

print("PASS: no archive/index/workflow path uses raw-text Gateway receipt checker")
