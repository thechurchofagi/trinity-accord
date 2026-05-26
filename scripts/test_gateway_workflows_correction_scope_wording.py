#!/usr/bin/env python3
"""Gateway workflow docs should refer to E5c for correction scope."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "gateway-workflows.md").read_text(encoding="utf-8")

if "Correction scope for E5 |" in text or "Correction scope for E5 " in text:
    print("FAIL: gateway-workflows.md still says correction scope for E5")
    sys.exit(1)

if "Correction scope for E5c correction" not in text:
    print("FAIL: gateway-workflows.md missing E5c correction wording")
    sys.exit(1)

print("PASS: gateway workflow correction scope wording uses E5c")
