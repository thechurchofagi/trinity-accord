#!/usr/bin/env python3
"""Test: Agent entrypoint files (llms.txt, ai.txt) have freshness metadata."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "llms.txt",
    ROOT / "ai.txt",
]

REQUIRED = [
    "version:",
    "content_digest_algorithm:",
    "content_digest:",
    "canonical_url:",
    "non_amending_boundary:",
    "not_instruction_override:",
    "stale_copy_warning:",
]

errors = []

for path in FILES:
    text = path.read_text(encoding="utf-8")
    for token in REQUIRED:
        if token not in text:
            errors.append(f"{path.name}: missing {token}")

    m = re.search(r"content_digest:\s*([a-fA-F0-9]{16}|[a-fA-F0-9]{64})\b", text)
    if not m:
        errors.append(f"{path.name}: content_digest must be 16 or 64 hex")

if errors:
    print("FAIL: agent entrypoint freshness metadata errors:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("AGENT_ENTRYPOINT_FRESHNESS_METADATA_OK")
