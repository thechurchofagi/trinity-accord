#!/usr/bin/env python3
"""REM-DOWNLOAD-001: Derive downloads freshness from sitemap."""
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
downloads = (ROOT / "downloads.md").read_text(encoding="utf-8")
sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")

ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
root = ET.fromstring(sitemap)

download_paths = set()
for url in root.findall("sm:url", ns):
    loc = url.find("sm:loc", ns)
    if loc is None or not loc.text:
        continue
    text = loc.text.strip()
    marker = "trinityaccord.org"
    if marker in text:
        path = text.split(marker, 1)[1]
    else:
        path = text
    if path.startswith("/downloads/"):
        if path.endswith((".py", ".sh", ".txt", ".json", ".zip", ".car")):
            continue
        download_paths.add(path.rstrip("/"))

missing = sorted(path for path in download_paths if path not in downloads)

required_api = [
    "/api/verification-materials.json",
    "/api/evidence-manifest.json",
    "/api/recovery-index.json",
    "/api/links.json",
]
missing_api = [p for p in required_api if p not in downloads]

if missing or missing_api:
    if missing:
        print("FAIL: downloads.md missing sitemap download pages:")
        for p in missing:
            print("  -", p)
    if missing_api:
        print("FAIL: downloads.md missing required API links:")
        for p in missing_api:
            print("  -", p)
    sys.exit(1)

print("PASS: downloads.md includes sitemap download pages and required evidence APIs")
