#!/usr/bin/env python3
"""Regression guards for public-surface defects found by the live site audit."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITEMAP_MODULE = ROOT / "scripts" / "generate_sitemap.py"


def fail(message: str) -> None:
    print(f"FAIL: {message}")
    raise SystemExit(1)


def markdown_h1s(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    front_matter = re.match(r"^---\s*\n.*?\n---", text, re.DOTALL)
    body = text[front_matter.end():] if front_matter else text
    headings: list[str] = []
    fence: str | None = None
    for line in body.splitlines():
        stripped = line.lstrip()
        if fence:
            if stripped.startswith(fence):
                fence = None
            continue
        if stripped.startswith("```"):
            fence = "```"
            continue
        if stripped.startswith("~~~"):
            fence = "~~~"
            continue
        if re.match(r"^#\s+\S", line):
            headings.append(line)
    return headings


def load_sitemap_module():
    spec = importlib.util.spec_from_file_location("generate_sitemap", SITEMAP_MODULE)
    if spec is None or spec.loader is None:
        fail("could not import scripts/generate_sitemap.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    sitemap = load_sitemap_module()
    excludes = sitemap.load_config().get("exclude", [])

    pages = set(sitemap.collect_pages(excludes))
    if "/deploy-recovery-trigger/" in pages:
        fail("published:false page is included by sitemap collection")

    if sitemap.yaml is not None and sitemap.parse_front_matter("title: `invalid-yaml") is not None:
        fail("invalid YAML front matter must be skipped, not published as a derived route")

    original_yaml = sitemap.yaml
    try:
        sitemap.yaml = None
        fallback_pages = set(sitemap.collect_pages(excludes))
    finally:
        sitemap.yaml = original_yaml
    if "/deploy-recovery-trigger/" in fallback_pages:
        fail("published:false page is included by fallback sitemap parser")

    expected_download_pages = {
        "/downloads/",
        "/downloads/arweave-bundle-verification/",
        "/downloads/gz2-notarial-certificate-github-release-backup-2026-05-14/",
        "/downloads/gz2-photos-arweave-2026-05-14/",
        "/downloads/redteam-audit-2026-05-08/",
        "/downloads/shenzhen-notary-arweave-2026-05-06/",
        "/downloads/shenzhen-notary-github-release-backup-2026-05-06/",
    }
    missing_downloads = sorted(expected_download_pages - pages)
    if missing_downloads:
        fail(f"public Downloads pages missing from sitemap collection: {missing_downloads}")

    for rel in [
        "naming.md",
        "independent-attestation.md",
        "for-skeptical-agents.md",
        "worth-preserving.md",
        "technical-historical-reference.md",
    ]:
        headings = markdown_h1s(ROOT / rel)
        if len(headings) != 1:
            fail(f"{rel} must have exactly one H1; found {headings}")

    archive = (ROOT / "archive_legacy_index_2025_09.md").read_text(encoding="utf-8")
    if "](#98369145)" in archive:
        fail("legacy homepage archive still contains the broken #98369145 fragment")
    if "https://ordinals.com/inscription/98369145" not in archive:
        fail("legacy homepage archive lacks the repaired Covenant proof target")

    print("PASS: public-surface live-audit regressions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
