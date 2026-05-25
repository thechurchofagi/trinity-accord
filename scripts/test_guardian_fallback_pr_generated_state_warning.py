#!/usr/bin/env python3
"""REM-GUARD-001: Guardian fallback PR warns about generated-state freshness."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / ".github/workflows/guardian-registry-auto-list.yml").read_text(encoding="utf-8")

required = [
    "Generated files",
    "generate_public_home_status.py --check",
    "generate_guardian_registry_page.py --check",
    "check_consistency.py",
]
missing = [x for x in required if x not in text]
if missing:
    print(f"FAIL: Guardian fallback PR does not warn/check generated state freshness: {missing}")
    sys.exit(1)

print("PASS: Guardian fallback PR warns about generated-state freshness")
