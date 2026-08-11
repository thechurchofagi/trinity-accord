#!/usr/bin/env python3
"""Static safety contract for the Zenodo standalone-PDF repair workflow."""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "repair-research-preprint-zenodo-files.yml"
AUTHORIZATION = (
    ROOT
    / "research"
    / "trinity-accord-design-and-limits"
    / "zenodo-file-repair-authorization-v1.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    text = WORKFLOW.read_text(encoding="utf-8")
    authorization = AUTHORIZATION.read_text(encoding="utf-8")
    required = [
        "permissions:\n  contents: read",
        "ZENODO_ACCESS_TOKEN: ${{ secrets.ZENODO_ACCESS_TOKEN }}",
        "TRINITY_RESEARCH_PREPRINT_FILE_REPAIR_V1_APPROVED",
        "scripts/test_research_preprint_zenodo_file_repair.py",
        "scripts/repair_research_preprint_zenodo_files.py",
        "https://zenodo.org/api/records/$RECORD_ID",
        "trinity-accord-design-and-limits-v1.1.pdf",
        "thechurchofagi/trinity-accord-ta-tr-2026-01-v1.1-zenodo.zip",
        "2facb19a2cfbd6d18573b7c1b18b52a7667cf0202e163c5d847ceb7a31cea4f2",
    ]
    missing = [marker for marker in required if marker not in text]
    require(not missing, f"workflow is missing safety markers: {missing}")

    forbidden = [
        "actions/newversion",
        "--method DELETE",
        "git push",
        "contents: write",
        "21675727",
    ]
    present = [marker for marker in forbidden if marker in text]
    require(not present, f"workflow contains prohibited behavior: {present}")

    for marker in [
        '"record_id": 21699878',
        '"doi": "10.5281/zenodo.21699878"',
        '"action": "add_existing_pdf_as_standalone_file"',
        '"create a new version"',
        '"change the paper bytes"',
    ]:
        require(marker in authorization, f"authorization is missing: {marker}")

    print("PASS: Zenodo standalone-PDF workflow is bounded and fail-closed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
