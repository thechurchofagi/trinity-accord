#!/usr/bin/env python3
"""Fail-closed contract for the TA-TR-2026-01 v1.1 release workflow."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/publish-research-preprint-release.yml"
PAPER = (
    ROOT
    / "research/trinity-accord-design-and-limits"
    / "trinity-accord-design-and-limits-v1.1.pdf"
)
RECORD = ROOT / "api/research-preprint.v1.json"
EXPECTED_PDF_SHA256 = (
    "2facb19a2cfbd6d18573b7c1b18b52a7667cf0202e163c5d847ceb7a31cea4f2"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    require(WORKFLOW.exists(), "research preprint release workflow is missing")
    require(PAPER.exists(), "v1.1 PDF is missing")
    require(RECORD.exists(), "research preprint API record is missing")

    workflow = WORKFLOW.read_text(encoding="utf-8")
    paper_sha256 = hashlib.sha256(PAPER.read_bytes()).hexdigest()
    record = json.loads(RECORD.read_text(encoding="utf-8"))

    require(
        paper_sha256 == EXPECTED_PDF_SHA256,
        f"v1.1 PDF SHA-256 drifted: {paper_sha256}",
    )
    require(record["version"] == "1.1", "research record version must remain 1.1")
    require(
        record["nonAuthoritativeInterpretation"] is True,
        "research record must remain non-authoritative",
    )
    require(
        record["primaryDraftingSystem"]["softwareVersion"] == "OpenAI GPT-5.6 Sol",
        "research record must identify GPT-5.6 Sol",
    )
    require(
        record["primaryDraftingSystem"]["configuration"] == "Extra High reasoning",
        "research record must identify Extra High reasoning",
    )
    require(
        record["primaryDraftingSystem"]["notScholarlyAuthor"] is True,
        "AI system must not be presented as the accountable scholarly author",
    )
    require(
        record["author"]["name"] == "Hongju Liu",
        "Hongju Liu must remain the responsible human author",
    )

    required_workflow_text = [
        "push:",
        "workflow_dispatch:",
        'paths:\n      - ".github/workflows/publish-research-preprint-release.yml"',
        "contents: write",
        "runs-on: ubuntu-24.04",
        "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
        "scripts/toolchain_provenance.py",
        "Authorize release writer",
        'thechurchofagi|"github-actions[bot]"',
        "ta-tr-2026-01-v1.1",
        EXPECTED_PDF_SHA256,
        "OpenAI GPT-5.6 Sol",
        "Extra High reasoning",
        "Non-authoritative interpretation notice.",
        "test \"$(git rev-parse HEAD)\" = \"$GITHUB_SHA\"",
        '--target "$GITHUB_SHA"',
        "--draft",
        "--draft=false",
        "resolve_tag_commit",
        "test \"$(resolve_tag_commit)\" = \"$GITHUB_SHA\"",
        "gh release upload",
        "gh release download",
        'test "$(jq -r \'.assets | length\' <<<"$release_json")" = "7"',
        "A Zenodo DOI is not claimed until an independently retrievable Zenodo record exists.",
    ]
    for needle in required_workflow_text:
        require(needle in workflow, f"release workflow missing contract text: {needle}")

    require("--clobber" not in workflow, "release assets must not be silently overwritten")
    require(
        "${{ inputs." not in workflow and "${{ github.event.inputs." not in workflow,
        "release workflow must not interpolate dispatch inputs into shell source",
    )

    print("PASS: research preprint release workflow is immutable and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
