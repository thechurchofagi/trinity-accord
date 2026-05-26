#!/usr/bin/env python3
"""generate_sitemap.py docs should match recursive api/**/*.json behavior."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "generate_sitemap.py").read_text(encoding="utf-8")

if "api/*.json files" in text:
    print("FAIL: generate_sitemap.py docstring still says api/*.json files")
    sys.exit(1)

if "api/**/*.json" not in text:
    print("FAIL: generate_sitemap.py docstring should mention api/**/*.json")
    sys.exit(1)

print("PASS: generate_sitemap.py docstring matches recursive API collection")
