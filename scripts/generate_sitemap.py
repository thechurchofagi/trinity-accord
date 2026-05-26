#!/usr/bin/env python3
"""Generate sitemap.xml from actual repository content.

Reads all Markdown pages with front matter permalinks, API JSON files,
and special root files to produce a complete sitemap.

Inputs:
  - All .md files with front matter (permalink)
  - api/*.json files
  - Root special files (llms.txt, ai.txt, etc.)

Outputs:
  - sitemap.xml
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
except ImportError:
    yaml = None

ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
CONFIG = ROOT / "_config.yml"
BASE_URL = "https://www.trinityaccord.org"

# Root-level special files to always include
ROOT_SPECIAL_FILES = [
    "llms.txt",
    "llms-full.txt",
    "ai.txt",
    "citation.cff",
    "metadata.json",
    "feed.xml",
    "robots.txt",
    "sitemap.xml",
]

# Root-level JSON files to include
ROOT_JSON_INCLUDE = [
    "memory-seed.json",
    "agent-map.json",
    "echo.json",
    "propagation.json",
    "verification.json",
    "version.json",
]


def load_config() -> dict:
    """Load _config.yml (with fallback if yaml not available)."""
    if yaml:
        try:
            with open(CONFIG, encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            pass
    # Fallback: parse exclude list manually
    content = CONFIG.read_text(encoding="utf-8")
    excludes = []
    in_exclude = False
    for line in content.split("\n"):
        if line.strip().startswith("exclude:"):
            in_exclude = True
            continue
        if in_exclude:
            m = re.match(r"\s+-\s+(.+)", line)
            if m:
                excludes.append(m.group(1).strip())
            elif line.strip() and not line.strip().startswith("#"):
                break
    return {"exclude": excludes}


def collect_pages(excludes: list[str]) -> list[str]:
    """Collect all page permalinks from .md files with front matter."""
    pages = []
    exclude_set = set(excludes)

    for root_dir in sorted(ROOT.iterdir()):
        if not root_dir.is_dir():
            continue
        root_str = str(root_dir.relative_to(ROOT))
        if root_str.startswith((".git", "node_modules", "_site", "vendor")):
            continue

        for md_file in sorted(root_dir.rglob("*.md")):
            if md_file.name.startswith("_"):
                continue

            rel = str(md_file.relative_to(ROOT))

            # Check excludes
            excluded = False
            for exc in exclude_set:
                if rel == exc or rel.startswith(exc + "/") or rel.startswith(exc):
                    excluded = True
                    break
            if excluded:
                continue

            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            if not content.startswith("---"):
                continue

            # Extract permalink from front matter
            fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if not fm_match:
                continue

            fm_text = fm_match.group(1)
            if yaml:
                try:
                    fm = yaml.safe_load(fm_text)
                except Exception:
                    continue
            else:
                # Fallback: extract permalink manually
                pm = re.search(r"permalink:\s*(.+)", fm_text)
                if pm:
                    fm = {"permalink": pm.group(1).strip().strip("\"'")}
                else:
                    fm = {}

            if not isinstance(fm, dict):
                continue

            permalink = fm.get("permalink")
            if permalink:
                pages.append(permalink)
            else:
                # No permalink: Jekyll derives URL from file path
                url_path = "/" + rel.replace(".md", "").lstrip("./") + "/"
                pages.append(url_path)

    # Also check root .md files
    for md_file in sorted(ROOT.glob("*.md")):
        if md_file.name.startswith("_"):
            continue
        rel = md_file.name
        excluded = any(rel == exc or rel.startswith(exc) for exc in exclude_set)
        if excluded:
            continue

        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if not content.startswith("---"):
            continue

        fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if not fm_match:
            continue

        fm_text = fm_match.group(1)
        if yaml:
            try:
                fm = yaml.safe_load(fm_text)
            except Exception:
                continue
        else:
            pm = re.search(r"permalink:\s*(.+)", fm_text)
            if not pm:
                continue
            fm = {"permalink": pm.group(1).strip().strip("\"'")}

        if not isinstance(fm, dict):
            continue

        permalink = fm.get("permalink")
        if permalink:
            pages.append(permalink)
        else:
            # No permalink: derive from filename
            url_path = "/" + rel.replace(".md", "") + "/"
            pages.append(url_path)

    return sorted(set(pages))


def collect_api_files() -> list[str]:
    """Collect public API JSON files recursively."""
    api_dir = ROOT / "api"
    if not api_dir.exists():
        return []

    files = []
    for f in sorted(api_dir.rglob("*.json")):
        if not f.is_file():
            continue
        rel = f.relative_to(ROOT).as_posix()
        files.append(f"/{rel}")
    return files


def collect_root_special() -> list[str]:
    """Collect root-level special files."""
    files = []
    for name in ROOT_SPECIAL_FILES:
        if (ROOT / name).exists():
            files.append(f"/{name}")
    for name in ROOT_JSON_INCLUDE:
        if (ROOT / name).exists():
            files.append(f"/{name}")
    return files


def generate_sitemap(all_paths: list[str]) -> str:
    """Generate sitemap XML content."""
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path in all_paths:
        url = f"{BASE_URL}{path}"
        lines.append(f"  <url><loc>{url}</loc></url>")
    lines.append("</urlset>")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate sitemap.xml")
    parser.add_argument("--check", action="store_true", help="Fail if sitemap.xml is not up to date")
    args = parser.parse_args()

    config = load_config()
    excludes = config.get("exclude", [])

    pages = collect_pages(excludes)
    api_files = collect_api_files()
    root_special = collect_root_special()

    all_paths = sorted(set(pages + api_files + root_special))
    expected_content = generate_sitemap(all_paths)

    if args.check:
        if SITEMAP.exists():
            actual = SITEMAP.read_text(encoding="utf-8")
            if actual != expected_content:
                # Count URLs for diagnostics
                actual_count = len(re.findall(r"<loc>", actual))
                expected_count = len(all_paths)
                print(f"sitemap.xml is out of date ({actual_count} URLs, expected {expected_count}).")
                return 1
        else:
            print("sitemap.xml does not exist.")
            return 1
        print(f"sitemap.xml is up to date ({len(all_paths)} URLs).")
        return 0

    SITEMAP.write_text(expected_content, encoding="utf-8")
    print(f"Updated sitemap.xml ({len(all_paths)} URLs: {len(pages)} pages, {len(api_files)} API, {len(root_special)} root)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
