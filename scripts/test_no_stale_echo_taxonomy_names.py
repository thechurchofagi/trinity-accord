#!/usr/bin/env python3
"""Current agent-facing route/config files must not contain stale Echo taxonomy names."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "api" / "gateway-builder-route-map.v1.json",
    ROOT / "api" / "agent-start.v1.json",
    ROOT / "api" / "agent-first-contact.json",
    ROOT / "api" / "agent-submit-gateway.json",
    ROOT / "api" / "agent-minimal-context.v1.json",
    ROOT / "api" / "agent-output-policy.v1.json",
    ROOT / "api" / "agent-task-router.v1.json",
    ROOT / "api" / "agent-required-reading.json",
    ROOT / "api" / "context-load-map.json",
    ROOT / "api" / "gateway-workflows.v1.json",
    ROOT / "agent-echo.md",
    ROOT / "agent-start.md",
    ROOT / "gateway-workflows.md",
    ROOT / "scripts" / "build_guardian_echo_payload.py",
    ROOT / "scripts" / "create_guardian_application.mjs",
]

STALE = [
    "E1_read_oriented_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
]

# Context keywords that indicate the stale value is mentioned as forbidden/warning,
# not used as an active canonical value.
SAFETY_CONTEXT = re.compile(
    r"(forbidden|do.not.use|invented|stale|not.use|never.use|禁止|不要使用)",
    re.IGNORECASE,
)

def is_in_safety_context(text: str, stale: str) -> bool:
    """Check if all occurrences of stale in text are within safety/forbidden context."""
    for m in re.finditer(re.escape(stale), text):
        # Look at surrounding ~200 chars for safety keywords
        start = max(0, m.start() - 200)
        end = min(len(text), m.end() + 200)
        ctx = text[start:end]
        if not SAFETY_CONTEXT.search(ctx):
            return False
    return True

ok = True
for path in FILES:
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8")
    for stale in STALE:
        if stale in text:
            if is_in_safety_context(text, stale):
                continue  # Allowed: mentioned as forbidden/warning
            print(f"FAIL: stale Echo taxonomy name {stale!r} found in {path.relative_to(ROOT)}")
            ok = False

if not ok:
    sys.exit(1)

print("PASS: no stale Echo taxonomy names in current route/config files")
