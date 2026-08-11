#!/usr/bin/env python3
"""Verify the scholarly discovery and dissemination package for TA-TR-2026-01."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "trinity-accord-design-and-limits"
DOI = "10.5281/zenodo.21699878"
PDF_SHA256 = "2facb19a2cfbd6d18573b7c1b18b52a7667cf0202e163c5d847ceb7a31cea4f2"
BRIEF_SHA256 = "57a4bda56a50e662313a1de0853393c61ecf7fd6348c73c442cffb56d5087036"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def strict_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    require(isinstance(value, dict), f"expected JSON object: {path}")
    return value


def main() -> int:
    original_pdf = RESEARCH / "trinity-accord-design-and-limits-v1.1.pdf"
    require(
        hashlib.sha256(original_pdf.read_bytes()).hexdigest() == PDF_SHA256,
        "published preprint bytes changed",
    )

    brief_pdf = RESEARCH / "trinity-accord-academic-brief-v1.1.pdf"
    require(brief_pdf.read_bytes().startswith(b"%PDF-"), "academic brief is not a PDF")
    require(
        hashlib.sha256(brief_pdf.read_bytes()).hexdigest() == BRIEF_SHA256,
        "academic brief bytes or deterministic build drifted",
    )
    require(brief_pdf.stat().st_size < 500_000, "academic brief exceeds crawler size target")

    brief = (RESEARCH / "academic-brief.md").read_text(encoding="utf-8")
    for marker in [
        DOI,
        "Limits and negative results",
        "Useful review questions",
        "not peer reviewed",
        "no interpretive authority",
        "not scholarly authorship",
    ]:
        require(marker in brief, f"academic brief is missing boundary: {marker}")

    ris = (RESEARCH / "citation.ris").read_text(encoding="utf-8")
    for marker in ["TY  - RPRT", "AU  - Liu, Hongju", f"DO  - {DOI}", "ER  -"]:
        require(marker in ris, f"RIS citation is missing: {marker}")

    csl = strict_json(RESEARCH / "citation.csl.json")
    require(csl.get("DOI") == DOI, "CSL-JSON DOI mismatch")
    require(csl.get("type") == "report", "CSL-JSON type mismatch")
    require(csl.get("author") == [{"family": "Liu", "given": "Hongju"}], "CSL author mismatch")

    hal = strict_json(RESEARCH / "hal-deposit-metadata.json")
    require(hal.get("submission_state") == "prepared_not_submitted", "HAL state overclaims")
    require(len(hal.get("blocking_requirements", [])) == 3, "HAL blockers missing")
    require(hal.get("related_data", {}).get("doi") == DOI, "HAL DOI mismatch")
    require(hal.get("peer_reviewed") is False, "HAL peer-review boundary missing")
    require(
        hal.get("independent_verification") is False,
        "HAL independent-verification boundary missing",
    )
    require(
        "does not claim that a HAL deposit exists" in hal.get("boundary", ""),
        "HAL non-submission boundary missing",
    )

    checksum_lines = (
        RESEARCH / "academic-materials-checksums.sha256"
    ).read_text(encoding="utf-8").splitlines()
    for line in checksum_lines:
        digest, filename = line.split("  ", 1)
        target = RESEARCH / filename
        require(target.is_file(), f"academic material is missing: {filename}")
        require(
            hashlib.sha256(target.read_bytes()).hexdigest() == digest,
            f"academic material checksum mismatch: {filename}",
        )

    layout = (ROOT / "_layouts" / "default.html").read_text(encoding="utf-8")
    for marker in [
        'name="citation_doi"',
        'name="citation_keywords"',
        'name="citation_fulltext_html_url"',
        'type="application/x-research-info-systems"',
        'type="application/vnd.citationstyles.csl+json"',
        '"propertyID": "DOI"',
    ]:
        require(marker in layout, f"scholarly layout metadata is missing: {marker}")

    machine = strict_json(ROOT / "api" / "research-preprint.v1.json")
    citation = machine.get("citation", {})
    require(citation.get("doi") == DOI, "machine citation DOI mismatch")
    require(citation.get("ris", "").endswith("/citation.ris"), "machine RIS link missing")
    require(
        citation.get("cslJson", "").endswith("/citation.csl.json"),
        "machine CSL-JSON link missing",
    )
    distribution = machine.get("distributionMaterials", {})
    require(
        distribution.get("academicBriefPdf", "").endswith(
            "/trinity-accord-academic-brief-v1.1.pdf"
        ),
        "machine academic brief link missing",
    )
    require(
        distribution.get("halDepositPackage", {}).get("state")
        == "prepared_not_submitted",
        "machine HAL state overclaims submission",
    )

    for relative, markers in {
        "research/index.md": ["academic brief", "Download RIS", "Download CSL-JSON"],
        "ai.txt": ["/academic-brief/", "trinity-accord-academic-brief-v1.1.pdf"],
        "llms.txt": ["/academic-brief/", "trinity-accord-academic-brief-v1.1.pdf"],
        "sitemap.xml": ["/academic-brief/", "citation.ris", "citation.csl.json"],
    }.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        for marker in markers:
            require(marker in text, f"{relative} is missing {marker}")

    print("PASS: academic dissemination package is complete and bounded")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
