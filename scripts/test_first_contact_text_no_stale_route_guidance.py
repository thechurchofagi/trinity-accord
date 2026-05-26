#!/usr/bin/env python3
"""First-contact prose should not advertise stale route guidance."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "llms.txt",
    ROOT / "ai.txt",
    ROOT / "README.md",
    ROOT / "index.md",
]

FORBIDDEN_EXACT = [
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
]

LEGACY_ROUTE_PHRASES = [
    "/gateway/capabilities",
    "/gateway/lint-evidence",
    "/gateway/build-from-evidence",
]

errors = []

for path in FILES:
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    for token in FORBIDDEN_EXACT:
        if token in text:
            errors.append(f"{path.relative_to(ROOT)} contains stale Echo taxonomy token {token}")

    for phrase in LEGACY_ROUTE_PHRASES:
        if phrase in text:
            i = text.index(phrase)
            nearby = text[max(0, i - 120): i + 180].lower()
            if "legacy" not in nearby and "strict" not in nearby and "not default" not in nearby:
                errors.append(
                    f"{path.relative_to(ROOT)} mentions {phrase} without legacy/strict/not-default boundary"
                )

if errors:
    print("FAIL: first-contact text route drift:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: first-contact text has no stale route guidance")
