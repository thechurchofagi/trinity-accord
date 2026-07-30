#!/usr/bin/env python3
"""Contract for the corrective Zenodo preprint release workflow."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "publish-corrective-zenodo-preprint-release.yml"
METADATA = (
    ROOT
    / "research"
    / "trinity-accord-design-and-limits"
    / "zenodo-deposit-metadata.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    require(WORKFLOW.exists(), "corrective Zenodo workflow is missing")
    require(not (ROOT / ".zenodo.json").exists(), "paper metadata must not replace project metadata on main")

    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "ARCHIVE_BRANCH: archive/ta-tr-2026-01-v1.1-zenodo",
        "RELEASE_TAG: ta-tr-2026-01-v1.1-zenodo",
        "scripts/toolchain_provenance.py",
        'metadata = dict(source["legacy_api_metadata"])',
        'Path(".zenodo.json").write_text(',
        'metadata["upload_type"] == "publication"',
        'metadata["publication_type"] == "preprint"',
        'git checkout --detach "$GITHUB_SHA"',
        'git push origin "$archive_sha:refs/heads/$ARCHIVE_BRANCH"',
        '"$METADATA_SOURCE"',
        '".zenodo.json"',
        '"make_latest":"false"',
        'test "$(jq -r \' .assets | length\' release.json)" = "8"'.replace("\' ", "\'"),
        'test "$(jq -r \' .assets | length\' <<<"$release_json")" = "8"'.replace("\' ", "\'"),
    ]
    missing = [marker for marker in required if marker not in text]
    require(not missing, f"workflow is missing required safety markers: {missing}")

    forbidden = [
        "git push --force",
        "git push -f",
        "--method DELETE",
        "delete-release",
        "refs/heads/main",
        "HEAD:main",
    ]
    present = [marker for marker in forbidden if marker in text]
    require(not present, f"workflow contains forbidden mutation patterns: {present}")

    metadata_source = json.loads(METADATA.read_text(encoding="utf-8"))
    metadata = metadata_source["legacy_api_metadata"]
    require(metadata_source["deposit_state"] == "prepared_not_submitted", "source state drifted")
    require(metadata["upload_type"] == "publication", "upload_type must be publication")
    require(metadata["publication_type"] == "preprint", "publication_type must be preprint")
    require(metadata["publication_date"] == "2026-07-29", "publication date drifted")
    require(metadata["version"] == "1.1", "version drifted")
    require(metadata["creators"] == [{
        "name": "Liu, Hongju",
        "affiliation": "Independent researcher, Shenzhen, China",
    }], "creator metadata drifted")
    require(metadata["license"] == "cc-by-4.0", "license drifted")
    require(metadata["access_right"] == "open", "access must remain open")

    print("CORRECTIVE_ZENODO_PREPRINT_RELEASE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
