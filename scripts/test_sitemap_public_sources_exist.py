#!/usr/bin/env python3
"""Every trinityaccord.org sitemap URL should have a local source/artifact.

This is intentionally source-level, not network-level. It verifies the GitHub
Pages source tree has files that correspond to the public URLs in sitemap.xml.
Supports Jekyll permalink front matter for URL-to-file mapping.
"""

from __future__ import annotations

import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"

HOSTS = {
    "trinityaccord.org",
    "www.trinityaccord.org",
}

# Some GitHub Pages/Jekyll generated paths are intentionally virtual.
# Keep this list small. Prefer adding a real source file or generator.
ALLOW_MISSING = {
    # Add explicit exceptions only with a comment and issue reference.
}


def _build_permalink_map() -> dict[str, Path]:
    """Scan .md files for Jekyll permalink front matter."""
    mapping: dict[str, Path] = {}
    for md in ROOT.rglob("*.md"):
        if any(part.startswith(".") for part in md.relative_to(ROOT).parts):
            continue
        if any(part.startswith("_") for part in md.relative_to(ROOT).parts):
            continue
        try:
            text = md.read_text(encoding="utf-8")[:2000]
        except Exception:
            continue
        if not text.startswith("---"):
            continue
        m = re.search(r"^permalink:\s*(.+?)$", text, re.MULTILINE)
        if m:
            permalink = m.group(1).strip().rstrip("/")
            if permalink:
                mapping[permalink] = md
    return mapping


_PERMALINK_MAP: dict[str, Path] | None = None


def get_permalink_map() -> dict[str, Path]:
    global _PERMALINK_MAP
    if _PERMALINK_MAP is None:
        _PERMALINK_MAP = _build_permalink_map()
    return _PERMALINK_MAP


def local_candidates(path: str) -> list[Path]:
    """Return plausible local source candidates for a sitemap path."""
    path = path.lstrip("/")
    if not path:
        return [ROOT / "index.md", ROOT / "index.html"]

    # Check permalink map first (permalink keys have leading slash)
    permalink_map = get_permalink_map()
    clean = path.rstrip("/")
    permalink_key = f"/{clean}"
    if permalink_key in permalink_map:
        return [permalink_map[permalink_key]]

    # Raw files such as /llms.txt, /ai.txt, /api/x.json, /feed.xml
    if "." in Path(path).name:
        return [ROOT / path]

    # Directory-style pretty URL.
    return [
        ROOT / clean / "index.md",
        ROOT / clean / "index.html",
        ROOT / f"{clean}.md",
        ROOT / f"{clean}.html",
        ROOT / clean / "README.md",
    ]


def main() -> None:
    tree = ET.parse(SITEMAP)
    ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

    errors: list[str] = []
    seen: set[str] = set()

    for loc_el in tree.findall(".//sm:loc", ns):
        loc = (loc_el.text or "").strip()
        if not loc:
            errors.append("empty <loc> in sitemap")
            continue
        if loc in seen:
            errors.append(f"duplicate sitemap URL: {loc}")
            continue
        seen.add(loc)

        parsed = urlparse(loc)
        if parsed.netloc not in HOSTS:
            errors.append(f"unexpected sitemap host: {loc}")
            continue

        if parsed.path in ALLOW_MISSING:
            continue

        candidates = local_candidates(parsed.path)
        if not any(p.exists() for p in candidates):
            rels = ", ".join(str(p.relative_to(ROOT)) for p in candidates)
            errors.append(f"sitemap URL has no local source/artifact: {loc} candidates=[{rels}]")

    if errors:
        print("FAIL: sitemap public source validation errors:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    print("PASS: sitemap public URLs have local source/artifact coverage")


if __name__ == "__main__":
    main()
