#!/usr/bin/env python3
"""Backfill the published Zenodo DOI into current research metadata.

The deposited v1.1 PDF and the pre-publication metadata snapshot remain
byte-identical to the Zenodo archive. Current discovery and citation surfaces
are updated to point to the minted DOI.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "trinity-accord-design-and-limits"
DOI = "10.5281/zenodo.21699878"
DOI_URL = f"https://doi.org/{DOI}"
RECORD_ID = 21699878
RECORD_URL = f"https://zenodo.org/records/{RECORD_ID}"
EARLIER_DOI = "10.5281/zenodo.21675727"
TITLE = (
    "Designing a Verifiable, Non-Amending Civilizational Memory Record "
    "for Future AI Agents: The Trinity Accord Case Study"
)
PDF_NAME = "trinity-accord-design-and-limits-v1.1.pdf"
PDF_SHA256 = "2facb19a2cfbd6d18573b7c1b18b52a7667cf0202e163c5d847ceb7a31cea4f2"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    require(count == 1, f"{path.relative_to(ROOT)} expected one replacement, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def update_landing_page() -> None:
    path = RESEARCH / "index.md"
    text = path.read_text(encoding="utf-8")
    require(DOI not in text, "landing page already contains DOI; refusing ambiguous rerun")

    text = text.replace(
        'citation_publication_date: "2026/07/29"\n',
        'citation_publication_date: "2026/07/29"\n'
        f'citation_doi: "{DOI}"\n',
        1,
    )
    text = text.replace(
        'article_identifier: "TA-TR-2026-01"\n',
        'article_identifier: "TA-TR-2026-01"\n'
        f'article_doi: "{DOI}"\n',
        1,
    )
    text = text.replace(
        "Version 1.1 - 29 July 2026 - Preprint, not peer reviewed<br>\n",
        "Version 1.1 - 29 July 2026 - Preprint, not peer reviewed<br>\n"
        f"DOI: [{DOI}]({DOI_URL})<br>\n",
        1,
    )
    text = text.replace(
        "[Download the current searchable PDF](./trinity-accord-design-and-limits-v1.1.pdf) | "
        "[Machine-readable record](/api/research-preprint.v1.json) | "
        "[Deposit metadata](./zenodo-deposit-metadata.json)",
        "[Download the current searchable PDF](./trinity-accord-design-and-limits-v1.1.pdf) | "
        f"[Zenodo record]({RECORD_URL}) | "
        "[Machine-readable record](/api/research-preprint.v1.json) | "
        "[Deposit metadata](./zenodo-deposit-metadata.json)",
        1,
    )
    version_note = (
        "**Version note:** Version 1.1 clarifies the paper's lack of interpretive authority "
        "and records the model's primary drafting contribution and the human responsibility "
        "boundary. The [version 1.0 PDF](./trinity-accord-design-and-limits-v1.pdf) remains "
        "preserved as the previous public version."
    )
    doi_note = (
        version_note
        + "\n\n"
        + f"**DOI note:** Zenodo record [{DOI}]({DOI_URL}) is the preferred scholarly "
        + "citation for Version 1.1. The downloadable v1.1 PDF remains byte-identical to "
        + "the file archived by Zenodo; the DOI is carried by the landing page, BibTeX, "
        + "machine-readable record, and arXiv source rather than by silently rewriting the "
        + "already deposited PDF."
    )
    require(version_note in text, "landing-page version note contract drifted")
    text = text.replace(version_note, doi_note, 1)
    path.write_text(text, encoding="utf-8")


def update_machine_record() -> None:
    path = ROOT / "api" / "research-preprint.v1.json"
    record = json.loads(path.read_text(encoding="utf-8"))
    require(record["identifier"] == "TA-TR-2026-01", "research record identifier drifted")
    require(record["status"]["doi"] is None, "research record DOI is not null before backfill")
    require(record["citation"]["doi"] is None, "citation DOI is not null before backfill")
    record["status"]["doi"] = DOI
    record["status"]["doiState"] = "published"
    record["citation"]["doi"] = DOI
    record["sameAs"] = [DOI_URL, RECORD_URL]
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_bibtex() -> None:
    path = RESEARCH / "citation.bib"
    replace_once(
        path,
        "  version     = {1.1},\n  url         = {https://www.trinityaccord.org/research/trinity-accord-design-and-limits/},\n",
        f"  version     = {{1.1}},\n  doi         = {{{DOI}}},\n"
        "  url         = {https://www.trinityaccord.org/research/trinity-accord-design-and-limits/},\n",
    )


def write_publication_record() -> None:
    path = RESEARCH / "zenodo-publication-record.json"
    require(not path.exists(), "Zenodo publication record already exists")
    record = {
        "schema": "trinity-accord.zenodo-publication.v1",
        "publication_state": "published",
        "publication_date": "2026-07-30",
        "resource_type": "publication-preprint",
        "title": TITLE,
        "creator": "Liu, Hongju",
        "version": "1.1",
        "technical_report": "TA-TR-2026-01",
        "doi": DOI,
        "doi_url": DOI_URL,
        "zenodo_record_id": RECORD_ID,
        "zenodo_record_url": RECORD_URL,
        "github_release_tag": "ta-tr-2026-01-v1.1-zenodo",
        "github_release_url": (
            "https://github.com/thechurchofagi/trinity-accord/releases/tag/"
            "ta-tr-2026-01-v1.1-zenodo"
        ),
        "archived_pdf": PDF_NAME,
        "archived_pdf_sha256": PDF_SHA256,
        "related_earlier_record": {
            "doi": EARLIER_DOI,
            "relationship": "earlier project-level metadata record",
            "preferred_for_this_paper": False,
        },
        "preferred_citation_record": True,
        "non_amending_boundary": True,
    }
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_readme() -> None:
    path = RESEARCH / "README-DEPOSIT.txt"
    content = f"""Trinity Accord Technical Report Deposit Package
================================================

Report:
  Designing a Verifiable, Non-Amending Civilizational Memory Record
  for Future AI Agents: The Trinity Accord Case Study

Identifier: TA-TR-2026-01
Version: 1.1
DOI: {DOI}
Zenodo record: {RECORD_URL}
Responsible human author and project initiator: Hongju Liu
Primary drafting system: ChatGPT with OpenAI GPT-5.6 Sol
Reasoning setting: Extra High
Date: 2026-07-29
Zenodo publication date: 2026-07-30
License: CC BY 4.0
Status: Published preprint; no interpretive authority; not peer reviewed;
        not independent verification

The package contains the searchable PDF, Markdown source, BibTeX citation,
full reference bibliography, license notice, the original prepared-deposit
metadata snapshot, the post-publication Zenodo record, and SHA-256 checksums.

Most prose, structure, literature synthesis, editing, consistency checking,
and document production were generated by the named primary drafting system
from instructions and project materials supplied by Hongju Liu. Hongju Liu
approved publication and accepts responsibility for the published version,
claims, citations, disclosures, licensing, and corrections. The model credit
is not scholarly authorship, personhood, independent verification, or OpenAI
endorsement.

Zenodo publication was completed through the repository's GitHub integration.
The preferred paper DOI is {DOI}. The earlier DOI {EARLIER_DOI}
describes an earlier project-level metadata record and is not the preferred
citation for this paper.

The file zenodo-deposit-metadata.json remains the exact pre-publication metadata
snapshot used to create the archive. Current publication facts are recorded in
zenodo-publication-record.json. The v1.1 PDF remains byte-identical to the file
archived by Zenodo; the minted DOI is backfilled into current discovery and
citation metadata without rewriting the deposited PDF.

This research package analyzes the Trinity Accord. It has no interpretive
authority and does not amend the three Bitcoin Originals.
"""
    path.write_text(content, encoding="utf-8")


def update_arxiv_builder() -> None:
    path = ROOT / "scripts" / "build_arxiv_research_preprint.py"
    replace_once(
        path,
        'LICENSE = "CC BY 4.0"\n',
        f'LICENSE = "CC BY 4.0"\nDEFAULT_DOI = "{DOI}"\n',
    )
    replace_once(
        path,
        '    parser.add_argument("--doi")\n',
        '    parser.add_argument("--doi", default=DEFAULT_DOI)\n',
    )


def write_sync_test() -> None:
    path = ROOT / "scripts" / "test_research_preprint_doi_sync.py"
    require(not path.exists(), "DOI sync test already exists")
    content = f'''#!/usr/bin/env python3
"""Fail-closed contract for the published Zenodo DOI backfill."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "trinity-accord-design-and-limits"
DOI = "{DOI}"
DOI_URL = "{DOI_URL}"
RECORD_URL = "{RECORD_URL}"
PDF_SHA256 = "{PDF_SHA256}"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {{message}}")


def main() -> int:
    landing = (RESEARCH / "index.md").read_text(encoding="utf-8")
    require(f'citation_doi: "{{DOI}}"' in landing, "landing-page citation DOI missing")
    require(f'article_doi: "{{DOI}}"' in landing, "landing-page article DOI missing")
    require(DOI_URL in landing and RECORD_URL in landing, "landing-page DOI links missing")
    require("byte-identical" in landing, "deposited-PDF immutability note missing")

    record = json.loads((ROOT / "api/research-preprint.v1.json").read_text(encoding="utf-8"))
    require(record["status"]["doi"] == DOI, "machine record DOI mismatch")
    require(record["status"]["doiState"] == "published", "machine DOI state mismatch")
    require(record["citation"]["doi"] == DOI, "machine citation DOI mismatch")
    require(record["sameAs"] == [DOI_URL, RECORD_URL], "machine record sameAs mismatch")

    bib = (RESEARCH / "citation.bib").read_text(encoding="utf-8")
    require("doi         = {" + DOI + "}," in bib, "BibTeX DOI missing")

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
        require(actual == expected, f"checksum mismatch for {{filename}}")

    print("PASS: Zenodo DOI is synchronized without rewriting the deposited PDF")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'''
    path.write_text(content, encoding="utf-8")


def wire_test() -> None:
    replace_once(
        ROOT / "scripts" / "run_ci_group.py",
        '        ["python3", "scripts/test_arxiv_research_preprint_builder.py"],\n',
        '        ["python3", "scripts/test_arxiv_research_preprint_builder.py"],\n'
        '        ["python3", "scripts/test_research_preprint_doi_sync.py"],\n',
    )
    replace_once(
        ROOT / "scripts" / "run_current_system_tests.py",
        '        "scripts/test_arxiv_research_preprint_builder.py",\n',
        '        "scripts/test_arxiv_research_preprint_builder.py",\n'
        '        "scripts/test_research_preprint_doi_sync.py",\n',
    )


def update_checksums() -> None:
    files = [
        PDF_NAME,
        "index.md",
        "citation.bib",
        "references.bib",
        "LICENSE-CC-BY-4.0.txt",
        "README-DEPOSIT.txt",
        "zenodo-deposit-metadata.json",
        "zenodo-publication-record.json",
    ]
    lines = []
    for name in files:
        path = RESEARCH / name
        require(path.exists(), f"checksum target missing: {name}")
        lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {name}")
    (RESEARCH / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    pdf = RESEARCH / PDF_NAME
    require(hashlib.sha256(pdf.read_bytes()).hexdigest() == PDF_SHA256, "input PDF hash drifted")
    update_landing_page()
    update_machine_record()
    update_bibtex()
    write_publication_record()
    update_readme()
    update_arxiv_builder()
    write_sync_test()
    wire_test()
    update_checksums()
    require(hashlib.sha256(pdf.read_bytes()).hexdigest() == PDF_SHA256, "PDF changed during DOI backfill")
    print(f"DOI backfill prepared: {DOI}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
