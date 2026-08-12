#!/usr/bin/env python3
"""Fail-closed closure contract for the completed TA-TR-2026-01 v1.1 release."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RETIRED_WORKFLOW = ROOT / ".github/workflows/publish-research-preprint-release.yml"
PAPER_DIR = ROOT / "research/trinity-accord-design-and-limits"
PAPER = PAPER_DIR / "trinity-accord-design-and-limits-v1.1.pdf"
RECORD = ROOT / "api/research-preprint.v1.json"
PUBLICATION = PAPER_DIR / "zenodo-publication-record.json"
DEPOSIT_SNAPSHOT = PAPER_DIR / "zenodo-deposit-metadata.json"
DOI_TEST = ROOT / "scripts/test_research_preprint_doi_sync.py"
DOI = "10.5281/zenodo.21699878"
DOI_URL = f"https://doi.org/{DOI}"
ZENODO_RECORD_URL = "https://zenodo.org/records/21699878"
EXPECTED_PDF_SHA256 = (
    "b391776db76f533799dc582f39af54d2e885fe2ed1982cfe3024a1400a403e9c"
)
ORIGINAL_ARCHIVE_PDF_SHA256 = (
    "2facb19a2cfbd6d18573b7c1b18b52a7667cf0202e163c5d847ceb7a31cea4f2"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    require(
        not RETIRED_WORKFLOW.exists(),
        "completed preprint release writer must remain retired",
    )
    require(PAPER.exists(), "published v1.1 PDF is missing")
    require(RECORD.exists(), "research preprint API record is missing")
    require(PUBLICATION.exists(), "Zenodo publication record is missing")
    require(DEPOSIT_SNAPSHOT.exists(), "pre-publication deposit snapshot is missing")
    require(DOI_TEST.exists(), "permanent DOI synchronization contract is missing")

    pdf_sha256 = hashlib.sha256(PAPER.read_bytes()).hexdigest()
    require(
        pdf_sha256 == EXPECTED_PDF_SHA256,
        f"published v1.1 PDF SHA-256 drifted: {pdf_sha256}",
    )

    record = json.loads(RECORD.read_text(encoding="utf-8"))
    require(record["version"] == "1.1", "research record version drifted")
    require(record["status"]["publication"] == "preprint", "publication type drifted")
    require(record["status"]["peerReviewed"] is False, "peer-review boundary drifted")
    require(record["status"]["doi"] == DOI, "published DOI drifted")
    require(record["status"]["doiState"] == "published", "DOI state drifted")
    require(record["citation"]["doi"] == DOI, "citation DOI drifted")
    require(
        record["sameAs"] == [DOI_URL, ZENODO_RECORD_URL],
        "published DOI sameAs links drifted",
    )
    require(record["nonAuthoritativeInterpretation"] is True, "authority boundary drifted")
    require(record["author"]["name"] == "Hongju Liu", "responsible author drifted")
    require(
        record["primaryDraftingSystem"]["softwareVersion"] == "OpenAI GPT-5.6 Sol",
        "primary drafting system drifted",
    )
    require(
        record["primaryDraftingSystem"]["configuration"] == "Extra High reasoning",
        "drafting-system configuration drifted",
    )
    require(
        record["primaryDraftingSystem"]["notScholarlyAuthor"] is True,
        "model authorship boundary drifted",
    )

    publication = json.loads(PUBLICATION.read_text(encoding="utf-8"))
    require(publication["publication_state"] == "published", "Zenodo state drifted")
    require(publication["doi"] == DOI, "Zenodo publication DOI drifted")
    require(publication["doi_url"] == DOI_URL, "Zenodo DOI URL drifted")
    require(
        publication["zenodo_record_url"] == ZENODO_RECORD_URL,
        "Zenodo record URL drifted",
    )
    require(
        publication["standalone_pdf_sha256"] == EXPECTED_PDF_SHA256,
        "Zenodo standalone PDF hash drifted",
    )
    require(
        publication["original_github_archive_pdf_sha256"]
        == ORIGINAL_ARCHIVE_PDF_SHA256,
        "original GitHub archive PDF hash drifted",
    )
    require(publication["correction"]["doi_unchanged"] is True, "DOI correction boundary drifted")
    require(publication["correction"]["canon_unchanged"] is True, "Canon correction boundary drifted")
    require(publication["preferred_citation_record"] is True, "preferred citation drifted")
    require(publication["non_amending_boundary"] is True, "non-amending boundary drifted")

    deposit = json.loads(DEPOSIT_SNAPSHOT.read_text(encoding="utf-8"))
    require(
        deposit["deposit_state"] == "prepared_not_submitted",
        "historical pre-publication deposit snapshot was rewritten",
    )
    require(
        "does not assert that a deposit or DOI exists" in deposit["boundary"],
        "historical deposit boundary drifted",
    )

    doi_test = DOI_TEST.read_text(encoding="utf-8")
    for marker in [DOI, DOI_URL, ZENODO_RECORD_URL, EXPECTED_PDF_SHA256]:
        require(marker in doi_test, f"permanent DOI contract missing marker: {marker}")

    print(
        "PASS: preprint release writer is retired; published DOI, Zenodo record, "
        "historical deposit snapshot, corrected PDF, and original archive remain fail-closed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
