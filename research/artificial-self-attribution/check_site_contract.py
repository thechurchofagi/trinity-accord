#!/usr/bin/env python3
"""Check the public paper's identity and discovery contract after integration."""
import json
import xml.etree.ElementTree as ET
from html.parser import HTMLParser

from integrate_site import BASE, ROOT, STEM, TITLE, VERSION, planned_files, require


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


def main():
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
    print("TA-TR-2026-08_PUBLICATION_METADATA_AND_DISCOVERY_PASS")


if __name__ == "__main__":
    main()
