#!/usr/bin/env python3
"""FUNC-STATUS-001: Status page freshness check."""
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

status = (ROOT / "status.md").read_text(encoding="utf-8")
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")

ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
root = ET.fromstring(sitemap)
actual_urls = len(root.findall("sm:url", ns))

# Check for stale hardcoded URL counts (older than current sitemap)
hardcoded = re.findall(r"(\d+)\s+URLs", status)
bad = []
for n in hardcoded:
    if int(n) != actual_urls:
        bad.append(n)

if bad:
    print(f"FAIL: status.md has stale hardcoded URL counts {bad}; sitemap has {actual_urls}")
    sys.exit(1)

print("PASS: status.md freshness checks passed")
