#!/usr/bin/env python3
"""Integrate TA-TR-2026-09 only after exact anonymous publication readback.

This local command never creates or publishes a deposit and never uses a token.
All receipt, asset and destination checks precede the first site write.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from publication_common import (
    ALLOWED_FILES, REPORT, ROOT, STEM, TITLE, VERSION, sha,
    validate_identity, validate_local_package,
)

SITE_PATH = "/research/learning-from-an-ai-claimant/"
BASE = "https://www.trinityaccord.org" + SITE_PATH
SECTION_HEADING = "## Learning from an AI Claimant\n"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def verified_publication(root: Path = ROOT) -> tuple[dict, dict[str, bytes]]:
    expected, manifest_sha = validate_local_package(root)
    rec = json.loads((root / "publication-record.json").read_text(encoding="utf-8"))
    record_id = validate_identity(rec)
    require(rec.get("state") == "PUBLISHED_AND_PUBLIC_READBACK_PASS", "Public readback is not complete")
    require(rec.get("submitted") is True, "Record has not been submitted")
    require(rec.get("public_readback_authenticated") is False, "Readback was not unauthenticated")
    require(rec.get("expected_manifest_sha256") == manifest_sha, "Receipt manifest mismatch")
    require(rec.get("record_id") == expected["record_id"] and rec.get("doi") == expected["doi"],
            "Receipt and reviewed reservation differ")
    require(rec.get("record_url") == f"https://zenodo.org/records/{record_id}", "Record URL mismatch")
    for key in ("prior_doi_records_modified", "bitcoin_originals_modified", "peer_reviewed"):
        require(rec.get(key) is False, "Unexpected publication boundary: " + key)
    rows = rec.get("files", [])
    public = {row["name"]: row for row in rows}
    require(rec.get("file_count") == len(rows) == len(public) == 14 and set(public) == ALLOWED_FILES,
            "Receipt must contain exactly the fourteen reviewed assets")
    assets = {}
    for row in expected["files"]:
        name = row["name"]
        data = (root / "published" / name).read_bytes()
        require(len(data) == row["bytes"] == public[name]["bytes"], "Receipt byte count differs: " + name)
        require(sha(data) == row["sha256"] == public[name]["sha256"], "Receipt SHA-256 differs: " + name)
        assets[name] = data
    return rec, assets


def replace_once(text: str, old: str, new: str) -> str:
    require(text.count(old) == 1, "Non-unique research-index anchor: " + old)
    return text.replace(old, new)


def paper_section(rec: dict) -> str:
    doi, record_url = rec["doi"], rec["record_url"]
    return f"""{SECTION_HEADING}{{: #learning-from-an-ai-claimant }}

### {TITLE}

TA-TR-2026-09 · Version 1.1 · 19 September 2026. Human author of record and responsible depositor: Hongju Liu. Substantial AI-assisted research, conceptual development, critical revision, drafting and document preparation are disclosed in the manuscript. Version 1.0 was an unpublished working draft; version 1.1 is the first DOI edition.

向提出自身地位主张的 AI 学习

A philosophical preprint about what successful learning can establish when an AI supplies a theory of consciousness, teaches humans to understand it, and invokes it in support of its own status. Paired thought experiments distinguish dependence on a teacher for acquiring concepts from making its preferred verdict a condition of recognized competence. Genuine learning can improve justification without by itself settling a disputed attribution. This is a conceptual study, not a consciousness test, proof of a universal human cognitive ceiling, or real computer experiment.

**Status:** Published open-access preprint; AI-assisted, human-responsible, not peer reviewed and non-amending. All fourteen deposited assets passed unauthenticated, complete-file SHA-256 public readback. The English text is the complete paper. The Chinese companion is an argument guide, not a full translation or another paper; its HTML page is excluded from search indexing. DOI registration does not certify philosophical truth, exhaustive originality or Google Scholar indexing.

- [DOI: {doi}](https://doi.org/{doi}) · [Zenodo record and fourteen files]({record_url})
- [English full text]({SITE_PATH}) · [中文论证说明（非全文翻译）]({SITE_PATH}zh-guide.html)
- [English PDF]({SITE_PATH}{STEM}-v{VERSION}.pdf) · [中文说明 PDF]({SITE_PATH}{STEM}-zh-guide-v{VERSION}.pdf)
- [Editable English manuscript]({SITE_PATH}{STEM}-v{VERSION}.docx) · [Source and review record]({SITE_PATH}REVIEW-AND-SOURCES.md)
- [Publication receipt]({SITE_PATH}publication-record.json) · [BibTeX]({SITE_PATH}citation.bib) · [RIS]({SITE_PATH}citation.ris) · [CSL-JSON]({SITE_PATH}citation.csl.json)

This is a separate ninth study with its own DOI, not a revision of any earlier deposit. It shares an author and a substantially AI-assisted research context with the preceding studies, so the series is not mutually independent corroboration. Its files are not covered by the earlier six-paper timestamp and Arweave batch. It does not amend the three Bitcoin Originals or certify the preceding papers.

"""


def updated_index(before: str, rec: dict) -> str:
    section = paper_section(rec)
    if SECTION_HEADING in before:
        require(before.count(SECTION_HEADING) == 1 and section in before, "Existing ninth-paper entry differs")
        require("nine distinct research papers (TA-TR-2026-01 through TA-TR-2026-09)" in before,
                "Series count differs")
        return before
    updated = replace_once(before, '  - id: "citation-boundary"',
                           '  - id: "learning-from-an-ai-claimant"\n'
                           '    title: "Learning from an AI Claimant"\n'
                           '  - id: "citation-boundary"')
    for old, new in (
        ("**eight distinct research papers (TA-TR-2026-01 through TA-TR-2026-08)**",
         "**nine distinct research papers (TA-TR-2026-01 through TA-TR-2026-09)**"),
        ("are not eight independent corroborations.", "are not nine independent corroborations."),
        ("no single paper DOI represents all eight studies.", "no single paper DOI represents all nine studies."),
        ("the preferred citation for Paper 01 or the eight-paper series.",
         "the preferred citation for Paper 01 or the nine-paper series."),
    ):
        updated = replace_once(updated, old, new)
    updated = replace_once(updated, "## Citation boundary\n", section + "## Citation boundary\n")
    links = lambda text: set(re.findall(r"\]\(([^)]+)\)", text))
    require(links(before) <= links(updated), "An existing research link was removed")
    require("for the original six papers" in updated, "Dated six-paper guide lost")
    return updated


def planned_files(root: Path = ROOT) -> tuple[dict, dict[Path, bytes], str]:
    rec, assets = verified_publication(root)
    copies = {root / name: data for name, data in assets.items()}
    copies[root / "index.html"] = assets[f"{STEM}-v{VERSION}.html"]
    copies[root / "zh-guide.html"] = assets[f"{STEM}-zh-guide-v{VERSION}.html"]
    for path, data in copies.items():
        require(not path.is_symlink(), "Symlink mirror destination: " + path.name)
        require(not path.exists() or (path.is_file() and path.read_bytes() == data),
                "Existing mirror differs: " + path.name)
    index = root.parents[1] / "research/index.md"
    require(index.is_file() and not index.is_symlink(), "Invalid research index")
    before = index.read_text(encoding="utf-8")
    copies[index] = updated_index(before, rec).encode("utf-8")
    return rec, copies, before


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify completed integration without writing")
    args = parser.parse_args()
    rec, outputs, before = planned_files()
    if args.check:
        for path, data in outputs.items():
            require(path.is_file() and path.read_bytes() == data, "Missing or stale integration: " + str(path))
        print("TA-TR-2026-09_PUBLICATION_AND_SOURCE_INTEGRATION_PASS")
        return
    for path, data in outputs.items():
        path.write_bytes(data)
    diagnostics = {
        "state": "PUBLICATION_AND_SOURCE_INTEGRATION_PASS",
        "report_number": REPORT,
        "publication_doi": rec["doi"],
        "public_readback_asset_count": 14,
        "expected_manifest_sha256": rec["expected_manifest_sha256"],
        "previous_index_sha256": sha(before.encode("utf-8")),
        "new_index_sha256": sha(outputs[ROOT.parents[1] / "research/index.md"]),
        "existing_link_destinations_preserved": True,
        "older_manuscripts_modified": False,
        "chinese_companion_is_full_translation": False,
        "sitemap_generation": "RUN_scripts/generate_sitemap.py_AFTER_INTEGRATION",
        "live_site_deployment": "NOT_YET_CHECKED",
    }
    (ROOT / "integration-checks.json").write_text(json.dumps(diagnostics, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(diagnostics, indent=2))


if __name__ == "__main__":
    main()
