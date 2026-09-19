#!/usr/bin/env python3
"""Check TA09's exact publication mirrors and single-paper discovery metadata."""
import argparse
import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

from integrate_site import BASE, REPORT, ROOT, SITE_PATH, STEM, TITLE, VERSION, planned_files, require, sha


class HeadMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name"):
            self.meta.setdefault(attrs["name"].lower(), []).append(attrs.get("content", ""))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))


def check_rendered_site(site_dir: Path, receipt: dict, outputs: dict) -> None:
    require(site_dir.is_dir(), "Generated site directory missing: " + str(site_dir))
    generated = site_dir / SITE_PATH.strip("/")
    records = {row["name"]: row for row in receipt["files"]}
    aliases = {"index.html": f"{STEM}-v{VERSION}.html",
               "zh-guide.html": f"{STEM}-zh-guide-v{VERSION}.html"}
    for path, data in outputs.items():
        if path.parent != ROOT:
            continue
        target = generated / path.name
        require(target.is_file() and not target.is_symlink(), "Generated mirror missing: " + path.name)
        actual = target.read_bytes()
        row = records[aliases.get(path.name, path.name)]
        require(actual == data and len(actual) == row["bytes"] and sha(actual) == row["sha256"],
                "Generated mirror differs from public receipt: " + path.name)


def main() -> None:
    pointer = ROOT / 'current-version.json'
    if pointer.exists():
        import subprocess
        import sys
        current = json.loads(pointer.read_text())
        require(current.get('version') == '1.2' and current.get('receipt_path') == 'versions/v1.2/publication-record.json',
                'Unsupported current edition pointer')
        subprocess.run([sys.executable, str(ROOT / 'versions/v1.2/check_site_contract.py'), *sys.argv[1:]], check=True)
        return
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, help="Also check actual Jekyll output")
    args = parser.parse_args()
    receipt, outputs, _ = planned_files()
    for path, data in outputs.items():
        require(path.is_file() and path.read_bytes() == data, "Integration differs: " + path.name)
    head = HeadMetadata()
    head.feed((ROOT / "index.html").read_text(encoding="utf-8"))
    require(head.canonicals == [BASE], "English canonical differs")
    for key, value in {
        "citation_title": TITLE,
        "citation_author": "Hongju Liu",
        "citation_doi": receipt["doi"],
        "citation_technical_report_number": REPORT,
        "citation_pdf_url": BASE + f"{STEM}-v{VERSION}.pdf",
        "citation_language": "en",
    }.items():
        require(head.meta.get(key) == [value], "Wrong scholarly metadata: " + key)
    require(len(head.meta.get("citation_publication_date", [])) == 1, "Missing publication date")
    require(not any("noindex" in value.lower() for value in head.meta.get("robots", [])),
            "English paper must remain indexable")
    guide = HeadMetadata()
    guide.feed((ROOT / "zh-guide.html").read_text(encoding="utf-8"))
    require(guide.canonicals == [BASE + "zh-guide.html"], "Guide canonical differs")
    require(any("noindex" in [token.strip().lower() for token in value.split(",")]
                for value in guide.meta.get("robots", [])), "Companion guide must be noindex")
    require(not any(key.startswith("citation_") for key in guide.meta),
            "Companion guide must not masquerade as scholarly full text")
    require(json.loads((ROOT / "citation.csl.json").read_text(encoding="utf-8"))["DOI"] == receipt["doi"],
            "CSL DOI differs")
    for name in ("citation.bib", "citation.ris"):
        require(receipt["doi"] in (ROOT / name).read_text(encoding="utf-8"), "Citation DOI missing: " + name)
    index = (ROOT.parents[1] / "research/index.md").read_text(encoding="utf-8")
    require(index.count('  - id: "learning-from-an-ai-claimant"') == 1, "Duplicate or missing TOC entry")
    require("for the original six papers" in index, "Dated six-paper guide lost")
    require("are not nine independent corroborations" in index, "Series evidence boundary lost")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    tree = ET.parse(ROOT.parents[1] / "sitemap.xml")
    urls = [e.text for e in tree.findall("s:url/s:loc", ns)]
    require(urls.count(BASE) == 1, "Sitemap must contain exactly one English canonical")
    require(not any(url.startswith(BASE) and url != BASE for url in urls),
            "Guide or duplicate publication asset indexed in sitemap")
    if args.site_dir is not None:
        check_rendered_site(args.site_dir, receipt, outputs)
        print("TA-TR-2026-09_RENDERED_PUBLICATION_MIRRORS_PASS")
    print("TA-TR-2026-09_PUBLICATION_METADATA_AND_DISCOVERY_PASS")


if __name__ == "__main__":
    main()
