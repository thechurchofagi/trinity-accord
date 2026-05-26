#!/usr/bin/env python3
"""Test: sitemap.xml includes key agent-facing entrypoints."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"

if not SITEMAP.exists():
    print("FAIL: sitemap.xml missing")
    sys.exit(1)

text = SITEMAP.read_text(encoding="utf-8")

REQUIRED = [
    "https://www.trinityaccord.org/llms.txt",
    "https://www.trinityaccord.org/llms-full.txt",
    "https://www.trinityaccord.org/ai.txt",
    "https://www.trinityaccord.org/agent-brief/",
    "https://www.trinityaccord.org/api/authority.json",
    "https://www.trinityaccord.org/api/echo-index.json",
    "https://www.trinityaccord.org/api/independent-attestation-index.json",
]

missing = [x for x in REQUIRED if x not in text]

if missing:
    print("FAIL: sitemap missing agent-facing entrypoints:")
    for x in missing:
        print("  -", x)
    sys.exit(1)

print("SITEMAP_AGENT_ENTRYPOINTS_OK")
