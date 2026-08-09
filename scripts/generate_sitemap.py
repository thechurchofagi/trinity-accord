#!/usr/bin/env python3
"""Generate complete and core discovery sitemaps.

Reads all Markdown pages with front matter permalinks, API JSON files recursively,
and special root files to produce the complete archival sitemap. A small,
hand-curated core sitemap gives search crawlers and agents a high-signal first
pass without removing any historical URL from the complete sitemap.

Inputs:
  - All .md files with front matter (permalink)
  - api/**/*.json files
  - Root special files (llms.txt, ai.txt, etc.)

Outputs:
  - sitemap.xml
  - sitemap-core.xml
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
CORE_SITEMAP = ROOT / "sitemap-core.xml"
CONFIG = ROOT / "_config.yml"
BASE_URL = "https://www.trinityaccord.org"

# Root-level special files to always include
ROOT_SPECIAL_FILES = [
    "llms.txt",
    "llms-full.txt",
    "ai.txt",
    "citation.cff",
    "CITATION.cff",
    "metadata.json",
    "feed.xml",
    "robots.txt",
    "sitemap-core.xml",
    "sitemap.xml",
    ".well-known/agent.json",
    ".well-known/trinity-accord.json",
    "research/trinity-accord-design-and-limits/trinity-accord-design-and-limits-v1.pdf",
    "research/trinity-accord-design-and-limits/trinity-accord-design-and-limits-v1.1.pdf",
    "research/trinity-accord-design-and-limits/zenodo-deposit-metadata.json",
    "research/trinity-accord-design-and-limits/citation.bib",
    "research/trinity-accord-design-and-limits/references.bib",
    "research/trinity-accord-design-and-limits/LICENSE-CC-BY-4.0.txt",
    "research/trinity-accord-design-and-limits/README-DEPOSIT.txt",
    "research/trinity-accord-design-and-limits/checksums.sha256",
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

# Current, high-signal discovery set. Historical and compatibility resources
# remain discoverable in sitemap.xml but are deliberately excluded here.
CORE_PATHS = [
    "/",
    "/agent-first-contact/",
    "/agent-start/",
    "/agent-brief/",
    "/authority/",
    "/verify/",
    "/verification-materials/",
    "/verification-procedures/",
    "/evidence-relationship-guide/",
    "/evidence-evolution/",
    "/for-skeptical-agents/",
    "/why-high-signal/",
    "/guardian-principles/",
    "/emergent-patterns/",
    "/status/",
    "/research/",
    "/research/trinity-accord-design-and-limits/",
    "/research/trinity-accord-design-and-limits/trinity-accord-design-and-limits-v1.1.pdf",
    "/llms.txt",
    "/llms-full.txt",
    "/ai.txt",
    "/metadata.json",
    "/memory-seed.json",
    "/agent-map.json",
    "/propagation.json",
    "/citation.cff",
    "/CITATION.cff",
    "/.well-known/agent.json",
    "/.well-known/trinity-accord.json",
    "/api/agent-first-contact.json",
    "/api/agent-minimal-context.v1.json",
    "/api/authority.json",
    "/api/seed-map.json",
    "/api/verification-procedures.v1.json",
    "/api/evidence-evolution-plan.v1.json",
    "/api/record-chain-status.json",
    "/api/public-home-status.json",
    "/api/research-preprint.v1.json",
    "/api/bitcoin-inscription-mirror-index.json",
    "/record-chain/indexes/record-index.json",
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


def parse_front_matter(fm_text: str) -> dict | None:
    """Parse page front matter, including publication state without PyYAML."""
    if yaml:
        try:
            parsed = yaml.safe_load(fm_text)
        except Exception:
            return None
        return parsed if isinstance(parsed, dict) else None

    fm: dict[str, object] = {}
    pm = re.search(r"(?m)^permalink:\s*(.+)$", fm_text)
    if pm:
        fm["permalink"] = pm.group(1).strip().strip("\"'")
    published = re.search(r"(?mi)^published:\s*(true|false)\s*$", fm_text)
    if published:
        fm["published"] = published.group(1).lower() == "true"
    sitemap = re.search(r"(?mi)^sitemap:\s*(true|false)\s*$", fm_text)
    if sitemap:
        fm["sitemap"] = sitemap.group(1).lower() == "true"
    return fm


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
            fm = parse_front_matter(fm_text)
            if fm is None:
                continue
            if fm.get("published") is False or fm.get("sitemap") is False:
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
        fm = parse_front_matter(fm_text)
        if fm is None:
            continue
        if fm.get("published") is False or fm.get("sitemap") is False:
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
        if name in {"sitemap.xml", "sitemap-core.xml"} or (ROOT / name).exists():
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


def report_drift(path: Path, expected_content: str, expected_paths: list[str]) -> bool:
    """Return True and print diagnostics when a sitemap is absent or stale."""
    if not path.exists():
        print(f"{path.name} does not exist.")
        return True

    actual = path.read_text(encoding="utf-8")
    if actual == expected_content:
        return False

    actual_urls = set(re.findall(r"<loc>(.*?)</loc>", actual))
    expected_urls = {f"{BASE_URL}{p}" for p in expected_paths}
    missing = sorted(expected_urls - actual_urls)
    extra = sorted(actual_urls - expected_urls)
    print(
        f"{path.name} is out of date "
        f"({len(actual_urls)} URLs, expected {len(expected_urls)})."
    )
    if missing:
        print(f"  Missing URLs ({len(missing)}):")
        for url in missing:
            print(f"    - {url}")
    if extra:
        print(f"  Extra URLs ({len(extra)}):")
        for url in extra:
            print(f"    + {url}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate complete and core sitemaps")
    parser.add_argument("--check", action="store_true", help="Fail if either sitemap is not up to date")
    args = parser.parse_args()

    config = load_config()
    excludes = config.get("exclude", [])

    pages = collect_pages(excludes)
    api_files = collect_api_files()
    root_special = collect_root_special()

    all_paths = sorted(set(pages + api_files + root_special))
    expected_content = generate_sitemap(all_paths)
    core_paths = sorted(set(CORE_PATHS))
    expected_core_content = generate_sitemap(core_paths)

    if args.check:
        stale = report_drift(SITEMAP, expected_content, all_paths)
        stale |= report_drift(CORE_SITEMAP, expected_core_content, core_paths)
        if stale:
            return 1
        print(f"sitemap.xml is up to date ({len(all_paths)} URLs).")
        print(f"sitemap-core.xml is up to date ({len(core_paths)} URLs).")
        return 0

    SITEMAP.write_text(expected_content, encoding="utf-8")
    CORE_SITEMAP.write_text(expected_core_content, encoding="utf-8")
    print(f"Updated sitemap.xml ({len(all_paths)} URLs: {len(pages)} pages, {len(api_files)} API, {len(root_special)} root)")
    print(f"Updated sitemap-core.xml ({len(core_paths)} high-signal URLs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
