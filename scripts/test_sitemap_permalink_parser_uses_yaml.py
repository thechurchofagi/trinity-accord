#!/usr/bin/env python3
"""sitemap permalink parser should prefer PyYAML when available."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "test_sitemap_permalink_matches_source.py").read_text(encoding="utf-8")

required = [
    "import yaml",
    "yaml.safe_load",
]

missing = [r for r in required if r not in text]
if missing:
    print("FAIL: sitemap permalink parser does not prefer YAML:")
    for m in missing:
        print("  -", m)
    sys.exit(1)

print("PASS: sitemap permalink parser uses YAML when available")
