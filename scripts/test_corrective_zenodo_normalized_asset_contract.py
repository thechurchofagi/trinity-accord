#!/usr/bin/env python3
"""Contract for GitHub-normalized Zenodo Release asset names.

GitHub first stored `.zenodo.json` as `default.zenodo.json`; a recovery attempt
also uploaded `zenodo.json`. Both aliases must be byte-identical to the archive
root `.zenodo.json` before the draft Release can be published.
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = (
    ROOT
    / ".github"
    / "workflows"
    / "publish-corrective-zenodo-normalized-assets.yml"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    require(WORKFLOW.exists(), "normalized Zenodo asset workflow is missing")
    require(
        not (ROOT / ".zenodo.json").exists(),
        "paper-specific .zenodo.json must remain outside main",
    )

    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "ARCHIVE_SHA: e4d23486a576783976857f925d23d8c8e7131c11",
        "RELEASE_TAG: ta-tr-2026-01-v1.1-zenodo",
        '".zenodo.json"',
        '"default.zenodo.json"',
        '"zenodo.json"',
        'test "${#sources[@]}" = "9"',
        "releases/$RELEASE_ID/assets?per_page=100",
        'test "$(jq \'length\' release-assets.json)" = "9"',
        'cmp "$source" "release-verify/$name"',
        'make_latest: "false"',
        'AUDIT_ISSUE: "786"',
        'state_reason: "completed"',
        "scripts/toolchain_provenance.py",
    ]
    missing = [marker for marker in required if marker not in text]
    require(not missing, f"workflow is missing required markers: {missing}")

    forbidden = [
        "--method DELETE",
        "git push --force",
        "git push -f",
        "refs/heads/main",
        "HEAD:main",
        ">/dev/null || true",
    ]
    present = [marker for marker in forbidden if marker in text]
    require(not present, f"workflow contains forbidden patterns: {present}")

    print("CORRECTIVE_ZENODO_NINE_ASSET_ALIAS_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
