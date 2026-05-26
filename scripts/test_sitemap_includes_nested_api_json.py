#!/usr/bin/env python3
"""sitemap.xml must include nested public api/**/*.json files."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")

required = [
    "https://www.trinityaccord.org/api/context-packs/nft-chronicle-context.json",
]

missing = [u for u in required if u not in sitemap]
if missing:
    print("FAIL: sitemap missing nested API JSON URL(s):")
    for u in missing:
        print("  -", u)
    sys.exit(1)

print("PASS: sitemap includes nested API JSON files")
