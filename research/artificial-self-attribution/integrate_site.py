#!/usr/bin/env python3
"""Mirror the actual TA-TR-2026-08 publication and extend the research index.

Run only after publish.py has recorded successful unauthenticated public
readback. This command performs no network operations or publication actions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT = "TA-TR-2026-08"
VERSION = "1.1"
TITLE = ("Evidence for Artificial Self Attribution: Language Training, "
         "Architecture, and the Limits of Self Reports")
STEM = "artificial-self-attribution"
SITE_PATH = "/research/artificial-self-attribution/"
BASE = "https://www.trinityaccord.org" + SITE_PATH
SECTION_HEADING = "## Evidence for Artificial Self Attribution\n"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def rows_by_name(rows: list[dict]) -> dict[str, dict]:
    result = {row["name"]: row for row in rows}
    require(len(result) == len(rows) == 14, "Publication must contain 14 unique assets")
    for name in result:
        require(Path(name).name == name and name not in (".", ".."), "Unsafe asset name")
    return result


def verified_publication(root: Path = ROOT) -> tuple[dict, dict[str, bytes]]:
    """Verify receipt, manifest and every exact local public-readback copy."""
    rec = json.loads((root / "publication-record.json").read_text())
    expected_bytes = (root / "EXPECTED-PUBLICATION.json").read_bytes()
    expected = json.loads(expected_bytes)
    require(rec.get("state") == "PUBLISHED_AND_PUBLIC_READBACK_PASS", "Public readback is not complete")
    require(rec.get("public_readback_authenticated") is False, "Readback was not unauthenticated")
    require(rec.get("submitted") is True, "Record has not been submitted")
    require(sha(expected_bytes) == rec.get("expected_manifest_sha256"), "Reviewed manifest changed")
    for source in (rec, expected):
        require(source.get("report_number") == REPORT, "Wrong report number")
        require(source.get("title") == TITLE, "Wrong publication title")
        require(source.get("version") == VERSION, "Wrong publication version")
        require(source.get("file_count") == 14, "Wrong publication file count")
    record_id = rec.get("record_id")
    require(isinstance(record_id, int) and record_id > 0, "Missing actual Zenodo record")
    doi = f"10.5281/zenodo.{record_id}"
    require(rec.get("doi") == expected.get("doi") == doi, "Publication DOI mismatch")
    require(expected.get("record_id") == record_id, "Manifest record mismatch")
    require(rec.get("record_url") == f"https://zenodo.org/records/{record_id}", "Record URL mismatch")
    for key in ("prior_doi_records_modified", "bitcoin_originals_modified", "peer_reviewed"):
        require(rec.get(key) is False, f"Unexpected publication boundary: {key}")
    manifest = rows_by_name(expected["files"])
    public = rows_by_name(rec["files"])
    require(set(manifest) == set(public), "Receipt assets differ from reviewed assets")
    require(set(manifest) == {p.name for p in (root / "published").iterdir()}, "Public mirror asset set differs")
    assets = {}
    for name, row in manifest.items():
        path = root / "published" / name
        require(path.is_file() and not path.is_symlink(), f"Invalid mirror asset: {name}")
        data = path.read_bytes()
        require(sha(data) == row["sha256"] == public[name]["sha256"], f"SHA-256 mismatch: {name}")
        require(len(data) == row["bytes"] == public[name]["bytes"], f"Byte-length mismatch: {name}")
        assets[name] = data
    return rec, assets


def replace_once(text: str, old: str, new: str) -> str:
    require(text.count(old) == 1, "Non-unique research-index anchor: " + old)
    return text.replace(old, new)


def current_series_word(text: str) -> str:
    """Accept the eighth-paper index and the ninth/tenth-paper extensions."""
    matches = [word for number, word in ((8, "eight"), (9, "nine"), (10, "ten"), (11, "eleven"), (12, "twelve"), (13, "thirteen"))
               if f"{word} distinct research papers (TA-TR-2026-01 through TA-TR-2026-{number:02d})" in text]
    require(len(matches) == 1, "Series count differs")
    return matches[0]


def paper_section(rec: dict) -> str:
    doi, record_url = rec["doi"], rec["record_url"]
    return f"""{SECTION_HEADING}{{: #evidence-for-artificial-self-attribution }}

### {TITLE}

TA-TR-2026-08 · Version 1.1 · 19 September 2026. Human author of record and responsible depositor: Hongju Liu. Substantial AI-assisted literature research, conceptual development, critical revision, drafting and translation are disclosed in the manuscript.

人工智能自我归属的证据边界

A philosophical preprint examining the selective effect of a source-based objection on a support relation: learning how a self report was generated can undercut that report's support for a claim without establishing that the claim is false or defeating independent mechanism evidence. Ten paired thought experiments distinguish operational identity, functional access, subjective experience, welfare interests and practical justification. The argument does not presuppose an answer to the question of AI consciousness. It is a conceptual study; no real computer experiments are required or claimed.

**Status:** Published open-access preprint; AI-assisted, human-responsible, not peer reviewed and non-amending. All fourteen deposited assets passed unauthenticated, complete-file SHA-256 public readback. The English and complete Chinese texts are one study. Publication does not certify exhaustive originality, empirical safety efficacy or Google Scholar indexing.

- [DOI: {doi}](https://doi.org/{doi}) · [Zenodo record and fourteen files]({record_url})
- [English full text]({SITE_PATH}) · [中文全文]({SITE_PATH}zh.html)
- [English PDF]({SITE_PATH}{STEM}-v{VERSION}.pdf) · [中文 PDF]({SITE_PATH}{STEM}-zh-v{VERSION}.pdf)
- [Publication receipt]({SITE_PATH}publication-record.json) · [Source comparison and substantive review]({SITE_PATH}REVIEW-AND-SOURCES.md)
- [BibTeX]({SITE_PATH}citation.bib) · [RIS]({SITE_PATH}citation.ris) · [CSL-JSON]({SITE_PATH}citation.csl.json)

This is a separate eighth study with its own DOI, not a revision of any earlier deposit. The papers share an author and a substantially AI-assisted research context: their number does not supply mutually independent corroboration. The eighth paper's new files are not covered by the earlier six-paper timestamp and Arweave batch. It does not amend the three Bitcoin Originals or make a finding about the truth of the preceding papers.

"""


def updated_index(before: str, rec: dict) -> str:
    section = paper_section(rec)
    if SECTION_HEADING in before:
        require(before.count(SECTION_HEADING) == 1 and section in before, "Existing eighth-paper entry differs")
        current_series_word(before)
        return before
    updated = replace_once(before, '  - id: "citation-boundary"',
                           '  - id: "evidence-for-artificial-self-attribution"\n'
                           '    title: "Evidence for Artificial Self Attribution"\n'
                           '  - id: "citation-boundary"')
    for old, new in (
        ("**seven distinct research papers (TA-TR-2026-01 through TA-TR-2026-07)**",
         "**eight distinct research papers (TA-TR-2026-01 through TA-TR-2026-08)**"),
        ("are not seven independent corroborations.", "are not eight independent corroborations."),
        ("no single paper DOI represents all seven studies.", "no single paper DOI represents all eight studies."),
        ("the preferred citation for Paper 01 or the seven-paper series.",
         "the preferred citation for Paper 01 or the eight-paper series."),
    ):
        updated = replace_once(updated, old, new)
    updated = replace_once(updated, "## Citation boundary\n", section + "## Citation boundary\n")
    links = lambda text: set(re.findall(r"\]\(([^)]+)\)", text))
    require(links(before) <= links(updated), "An existing research link was removed")
    return updated


def planned_files(root: Path = ROOT) -> tuple[dict, dict[Path, bytes], str]:
    rec, assets = verified_publication(root)
    repo = root.parents[1]
    copies = {}
    for lang, dest in (("", "index.html"), ("-zh", "zh.html")):
        stem = f"{STEM}{lang}-v{VERSION}"
        copies[root / dest] = assets[stem + ".html"]
        copies[root / (stem + ".pdf")] = assets[stem + ".pdf"]
    for name in ("citation.bib", "citation.ris", "citation.csl.json", "README-LICENSE.txt"):
        copies[root / name] = assets[name]
    for path, data in copies.items():
        require(not path.exists() or path.read_bytes() == data, f"Existing mirror differs: {path.name}")
    index = repo / "research/index.md"
    before = index.read_text()
    copies[index] = updated_index(before, rec).encode()
    return rec, copies, before


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify completed integration without writing")
    args = parser.parse_args()
    rec, outputs, before = planned_files()
    if args.check:
        for path, data in outputs.items():
            require(path.exists() and path.read_bytes() == data, f"Missing or stale integration: {path}")
        print("PUBLICATION_AND_SOURCE_INTEGRATION_PASS")
        return
    # All publication and destination checks precede the first write.
    for path, data in outputs.items():
        path.write_bytes(data)
    diagnostics = {
        "state": "PUBLICATION_AND_SOURCE_INTEGRATION_PASS",
        "report_number": REPORT,
        "publication_doi": rec["doi"],
        "public_readback_asset_count": 14,
        "expected_manifest_sha256": rec["expected_manifest_sha256"],
        "previous_index_sha256": sha(before.encode()),
        "new_index_sha256": sha(outputs[ROOT.parents[1] / "research/index.md"]),
        "existing_link_destinations_preserved": True,
        "older_manuscripts_modified": False,
        "sitemap_generation": "RUN_scripts/generate_sitemap.py_AFTER_INTEGRATION",
        "live_site_deployment": "NOT_YET_CHECKED",
    }
    (ROOT / "integration-checks.json").write_text(json.dumps(diagnostics, indent=2) + "\n")
    print(json.dumps(diagnostics, indent=2))
    print("Next: python3 scripts/generate_sitemap.py")


if __name__ == "__main__":
    main()
