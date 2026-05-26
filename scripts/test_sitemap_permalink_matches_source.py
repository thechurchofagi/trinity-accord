#!/usr/bin/env python3
"""Markdown permalinks should align with sitemap pretty URLs where applicable."""
from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"

FRONT = re.compile(r"^---\n(.*?)\n---\n", re.DOTALL)

def read_front_matter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    m = FRONT.match(text)
    if not m:
        return {}

    fm_text = m.group(1)

    if yaml is not None:
        try:
            data = yaml.safe_load(fm_text) or {}
        except Exception:
            return {}
        return data if isinstance(data, dict) else {}

    out = {}
    for line in fm_text.splitlines():
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out

def candidates(path: str) -> list[Path]:
    p = path.lstrip("/").rstrip("/")
    if not p:
        return [ROOT / "index.md"]
    return [
        ROOT / f"{p}.md",
        ROOT / p / "index.md",
        ROOT / p / "README.md",
    ]

tree = ET.parse(SITEMAP)
ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
errors = []

for loc_el in tree.findall(".//sm:loc", ns):
    loc = (loc_el.text or "").strip()
    parsed = urlparse(loc)
    path = parsed.path

    # Only pretty HTML pages, not raw artifacts.
    if "." in Path(path).name:
        continue

    src = next((c for c in candidates(path) if c.exists()), None)
    if not src:
        continue

    fm = read_front_matter(src)
    permalink = fm.get("permalink")
    if permalink and permalink.rstrip("/") != path.rstrip("/"):
        errors.append(
            f"{src.relative_to(ROOT)} permalink {permalink!r} does not match sitemap path {path!r}"
        )

if errors:
    print("FAIL: sitemap permalink mismatch:")
    for e in errors:
        print("  -", e)
    sys.exit(1)

print("PASS: sitemap pretty URLs match source permalinks where declared")
