#!/usr/bin/env python3
"""Test corrections-index is mandatory in recovery (TA-REDTEAM-2026-014).

Checks:
- RECOVERY.md says corrections-index is mandatory before accepting recovered state
- recovery-index mandatory_recovery_steps contains check_corrections_index
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors = []

    # Check RECOVERY.md
    recovery_path = ROOT / "RECOVERY.md"
    if recovery_path.exists():
        text = recovery_path.read_text(encoding="utf-8")
        if "mandatory" not in text.lower() or "corrections-index" not in text:
            errors.append("RECOVERY.md does not clearly state corrections-index is mandatory")
        # Check for the specific mandatory step language
        if "Do not skip" not in text and "mandatory step" not in text.lower():
            errors.append("RECOVERY.md does not emphasize corrections-index as mandatory step")
    else:
        errors.append("RECOVERY.md missing")

    # Check recovery-index.json
    ri_path = ROOT / "api" / "recovery-index.json"
    if ri_path.exists():
        ri = json.loads(ri_path.read_text(encoding="utf-8"))
        steps = ri.get("mandatory_recovery_steps", [])
        if "check_corrections_index" not in steps:
            errors.append("recovery-index mandatory_recovery_steps missing check_corrections_index")
        req_files = ri.get("required_recovery_files", [])
        if not any("corrections-index" in f for f in req_files):
            errors.append("recovery-index required_recovery_files missing corrections-index")
    else:
        errors.append("api/recovery-index.json missing")

    if errors:
        print("CORRECTIONS_REQUIRED_FAIL")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("CORRECTIONS_REQUIRED_OK")


if __name__ == "__main__":
    main()
