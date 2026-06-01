#!/usr/bin/env python3
"""Gateway workflow final checklist must include post-submit readback before exit."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
doc = (ROOT / "gateway-workflows.md").read_text(encoding="utf-8")

m = re.search(r"## Final checklist.*$", doc, flags=re.S)
section = m.group(0) if m else ""

if not section:
    print("FAIL: Final checklist section not found")
    sys.exit(1)

required = [
    "Before submission:",
    "Before leaving:",
    "I read `issue_url` when tool access allowed.",
    "I checked the route-specific public status/index target.",
    "I read `/api/public-home-status.json` when public status is claimed.",
    "I reported `archive_status_if_known`.",
    "I reported whether public status readback was performed.",
    "I did not claim archived from `issue_created` alone.",
    "I did not claim public status updated without public status/index readback.",
    "I did not claim active Guardian status without `/api/guardian-registry.json` readback when applicable.",
    "I stated remaining uncertainty and next step or stop reason.",
]

errors = [phrase for phrase in required if phrase not in section]

if errors:
    print("FAIL: Final checklist missing post-submit items:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: final checklist includes post-submit readback before exit")
