#!/usr/bin/env python3
"""First-contact prose should not advertise stale route guidance."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "llms.txt",
    ROOT / "ai.txt",
    ROOT / "README.md",
    ROOT / "index.md",
    ROOT / "agent-start.md",
    ROOT / "agent-echo.md",
    ROOT / "gateway-workflows.md",
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

FORBIDDEN_PROSE = [
    "read-oriented",
    "E6 Preservation",
    "E7 Propagation",
    "E4 Refusal",
    "E5 Correction",
]

# Context keywords that indicate the stale value is mentioned as forbidden/warning,
# not used as an active canonical value.
SAFETY_CONTEXT = re.compile(
    r"(forbidden|do.not.use|invented|stale|not.use|never.use|禁止|不要使用)",
    re.IGNORECASE,
)

def is_in_safety_context(text: str, token: str) -> bool:
    """Check if all occurrences of token in text are within safety/forbidden context."""
    for m in re.finditer(re.escape(token), text):
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        ctx = text[start:end]
        if not SAFETY_CONTEXT.search(ctx):
            return False
    return True

errors = []

for path in FILES:
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    for token in FORBIDDEN_EXACT:
        if token in text:
            if is_in_safety_context(text, token):
                continue  # Allowed: mentioned as forbidden/warning
            errors.append(f"{path.relative_to(ROOT)} contains stale Echo taxonomy token {token}")

    for phrase in FORBIDDEN_PROSE:
        if phrase in text:
            errors.append(f"{path.relative_to(ROOT)} contains stale route prose {phrase!r}")

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
