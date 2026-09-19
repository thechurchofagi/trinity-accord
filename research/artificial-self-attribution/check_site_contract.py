#!/usr/bin/env python3
"""Check the public paper's identity and discovery contract after integration."""
import argparse
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

from integrate_site import BASE, ROOT, SITE_PATH, STEM, TITLE, VERSION, planned_files, require, sha


class HeadMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta" and attrs.get("name", "").startswith("citation_"):
            self.meta.setdefault(attrs["name"], []).append(attrs.get("content"))
        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href"))


def check_rendered_site(site_dir, receipt, expected_outputs):
    """Check exactly the two full-text pages and two PDF mirrors after Jekyll."""
    site_dir = Path(site_dir)
    require(site_dir.is_dir(), f"Generated site directory missing: {site_dir}")
    generated = site_dir / SITE_PATH.strip("/")
    records = {row["name"]: row for row in receipt["files"]}
    for page, suffix in (("index.html", ""), ("zh.html", "-zh")):
        name = f"{STEM}{suffix}-v{VERSION}"
        for site_name, asset_name in ((page, name + ".html"), (name + ".pdf", name + ".pdf")):
            path = generated / site_name
            require(path.is_file() and not path.is_symlink(), f"Generated publication asset missing or invalid: {path}")
            actual = path.read_bytes()
            source = expected_outputs[ROOT / site_name]
            record = records[asset_name]
            require(actual == source, f"Generated publication bytes differ from source: {site_name}")
            require(len(actual) == record["bytes"] and sha(actual) == record["sha256"],
                    f"Generated publication asset differs from verified receipt: {site_name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-dir", type=Path, help="Also check the actual Jekyll output directory")
    args = parser.parse_args()
    receipt, expected_outputs, _ = planned_files()
    for path, data in expected_outputs.items():
        require(path.exists() and path.read_bytes() == data, f"Integration differs: {path.name}")
    for lang, page, suffix in (("en", "index.html", ""), ("zh", "zh.html", "-zh")):
        head = HeadMetadata()
        head.feed((ROOT / page).read_text())
        require(head.canonicals == [BASE + ("" if lang == "en" else page)], "Canonical URL mismatch")
        for key, value in {
            "citation_doi": receipt["doi"],
            "citation_author": "Hongju Liu",
            "citation_technical_report_number": "TA-TR-2026-08",
            "citation_pdf_url": BASE + f"{STEM}{suffix}-v{VERSION}.pdf",
            "citation_language": lang,
        }.items():
            require(head.meta.get(key) == [value], f"Wrong {lang} scholarly metadata: {key}")
        require(len(head.meta.get("citation_publication_date", [])) == 1, "Missing publication date")
        if lang == "en":
            require(head.meta.get("citation_title") == [TITLE], "Wrong English scholarly title")
    require(json.loads((ROOT / "citation.csl.json").read_text())["DOI"] == receipt["doi"], "CSL DOI mismatch")
    for name in ("citation.bib", "citation.ris"):
        require(receipt["doi"] in (ROOT / name).read_text(), f"Citation DOI missing: {name}")
    index = (ROOT.parents[1] / "research/index.md").read_text()
    require(index.count('  - id: "evidence-for-artificial-self-attribution"') == 1, "Duplicate or missing TOC")
    require("for the original six papers" in index, "Dated six-paper guide lost")
    require("are not eight independent corroborations" in index, "Series evidence boundary lost")
    tree = ET.parse(ROOT.parents[1] / "sitemap.xml")
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = [e.text for e in tree.findall("s:url/s:loc", ns)]
    for url in (BASE, BASE + "zh.html"):
        require(urls.count(url) == 1, "Sitemap must contain exactly one canonical: " + url)
    require(not any(url.startswith(BASE + "published/") or url == BASE + "index.html" for url in urls),
            "Duplicate publication source indexed")
    if args.site_dir is not None:
        check_rendered_site(args.site_dir, receipt, expected_outputs)
        print("TA-TR-2026-08_RENDERED_FULL_TEXT_AND_PDF_MIRRORS_PASS")
    print("TA-TR-2026-08_PUBLICATION_METADATA_AND_DISCOVERY_PASS")


if __name__ == "__main__":
    main()
