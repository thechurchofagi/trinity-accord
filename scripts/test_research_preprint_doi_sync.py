#!/usr/bin/env python3
"""Fail-closed contract for the published Zenodo DOI backfill."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "trinity-accord-design-and-limits"
DOI = "10.5281/zenodo.21699878"
DOI_URL = "https://doi.org/10.5281/zenodo.21699878"
RECORD_URL = "https://zenodo.org/records/21699878"
PDF_SHA256 = "2facb19a2cfbd6d18573b7c1b18b52a7667cf0202e163c5d847ceb7a31cea4f2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    landing = (RESEARCH / "index.md").read_text(encoding="utf-8")
    require(f'citation_doi: "{DOI}"' in landing, "landing-page citation DOI missing")
    require(f'article_doi: "{DOI}"' in landing, "landing-page article DOI missing")
    require(DOI_URL in landing and RECORD_URL in landing, "landing-page DOI links missing")
    require("byte-identical" in landing, "deposited-PDF immutability note missing")

    research_index = (ROOT / "research" / "index.md").read_text(encoding="utf-8")
    require(DOI_URL in research_index, "research index DOI URL missing")
    require(RECORD_URL in research_index, "research index Zenodo record URL missing")
    require("Published open-access preprint" in research_index, "research index publication state missing")
    require("10.5281/zenodo.21675727" in research_index, "earlier-record citation boundary missing")

    ai_text = (ROOT / "ai.txt").read_text(encoding="utf-8")
    require(DOI_URL in ai_text, "ai.txt DOI URL missing")
    require(RECORD_URL in ai_text, "ai.txt Zenodo record URL missing")

    record = json.loads((ROOT / "api/research-preprint.v1.json").read_text(encoding="utf-8"))
    require(record["status"]["doi"] == DOI, "machine record DOI mismatch")
    require(record["status"]["doiState"] == "published", "machine DOI state mismatch")
    require(record["citation"]["doi"] == DOI, "machine citation DOI mismatch")
    require(record["sameAs"] == [DOI_URL, RECORD_URL], "machine record sameAs mismatch")

    bib = (RESEARCH / "citation.bib").read_text(encoding="utf-8")
    require(DOI in bib and "doi         =" in bib, "BibTeX DOI missing")

    publication = json.loads((RESEARCH / "zenodo-publication-record.json").read_text(encoding="utf-8"))
    require(publication["publication_state"] == "published", "Zenodo state mismatch")
    require(publication["doi"] == DOI, "Zenodo publication DOI mismatch")
    require(publication["zenodo_record_url"] == RECORD_URL, "Zenodo record URL mismatch")
    require(publication["archived_pdf_sha256"] == PDF_SHA256, "recorded PDF hash mismatch")

    deposit = json.loads((RESEARCH / "zenodo-deposit-metadata.json").read_text(encoding="utf-8"))
    require(deposit["deposit_state"] == "prepared_not_submitted", "deposit snapshot was rewritten")
    require("does not assert that a deposit or DOI exists" in deposit["boundary"], "deposit boundary drifted")

    pdf_hash = hashlib.sha256((RESEARCH / "trinity-accord-design-and-limits-v1.1.pdf").read_bytes()).hexdigest()
    require(pdf_hash == PDF_SHA256, "published v1.1 PDF bytes changed")

    sys.path.insert(0, str(ROOT / "scripts"))
    import build_arxiv_research_preprint as builder
    require(builder.DEFAULT_DOI == DOI, "arXiv builder default DOI mismatch")

    checksum_lines = (RESEARCH / "checksums.sha256").read_text(encoding="utf-8").splitlines()
    for line in checksum_lines:
        expected, filename = line.split("  ", 1)
        actual = hashlib.sha256((RESEARCH / filename).read_bytes()).hexdigest()
        require(actual == expected, f"checksum mismatch for {filename}")

    print("PASS: Zenodo DOI is synchronized without rewriting the deposited PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
