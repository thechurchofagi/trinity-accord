#!/usr/bin/env python3
"""Contract for the final corrective Zenodo Release completion workflow."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "complete-corrective-zenodo-release.yml"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(f"FAIL: {message}")


def main() -> int:
    require(WORKFLOW.exists(), "final corrective Zenodo workflow is missing")
    require(
        not (ROOT / ".zenodo.json").exists(),
        "paper-specific .zenodo.json must not be committed to main",
    )

    text = WORKFLOW.read_text(encoding="utf-8")
    required = [
        "ARCHIVE_BRANCH: archive/ta-tr-2026-01-v1.1-zenodo",
        "ARCHIVE_SHA: e4d23486a576783976857f925d23d8c8e7131c11",
        "RELEASE_TAG: ta-tr-2026-01-v1.1-zenodo",
        "scripts/toolchain_provenance.py",
        "releases/$RELEASE_ID/assets?per_page=100",
        "--write-out '%{http_code}'",
        'if [ "$http_code" = "422" ]; then',
        'test "$matches" = "1"',
        'test "$state" = "uploaded"',
        'test "$(jq \'length\' release-assets.json)" = "8"',
        'cmp "$source" "release-verify/$name"',
        'make_latest: "false"',
        'AUDIT_ISSUE: "786"',
        'state_reason: "completed"',
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

    print("COMPLETE_CORRECTIVE_ZENODO_RELEASE_CONTRACT_OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
