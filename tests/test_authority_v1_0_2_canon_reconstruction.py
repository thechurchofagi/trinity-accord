from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
CANON = ROOT / "archive/authority-manifest/authority-v1.0.2-canon.json"
EXPECTED_SHA256 = "7d6ac9d3184bb5b0bbaf8217354799efef68669c21b4180e28ec06b0c57439e6"


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_exact_canon_is_reproducible_and_bound_to_signed_readback() -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts/rebuild_authority_v1_0_2_canon.py")],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert CANON.stat().st_size == 9174
    assert hashlib.sha256(CANON.read_bytes()).hexdigest() == EXPECTED_SHA256
    assert CANON.read_bytes()[-1:] == b"}"


def test_asset_manifest_no_longer_reports_a_false_repository_mismatch() -> None:
    manifest = load("archive/hash-manifest.json")
    entry = next(
        item
        for item in manifest["files"]
        if item["path"] == "archive/authority-manifest/authority-v1.0.2-canon.json"
    )
    assert entry["sha256"] == entry["expected_sha256"] == EXPECTED_SHA256
    assert entry["size_bytes"] == 9174
    assert entry["verified"] is True
    assert "hash_mismatch" not in entry
    assert manifest["summary"]["repo_files_hash_mismatch"] == 0
    assert manifest["summary"]["hash_mismatch"] == 0


def test_legacy_pointer_registry_records_exact_canonical_recovery() -> None:
    registry = load("archive/legacy-pointers/index.json")
    columns = registry["arweave_columns"]
    rows = [dict(zip(columns, row, strict=True)) for row in registry["arweave"]]
    entry = next(item for item in rows if item["txid"] == "TvmjyJBq5ZoGv-tmX0aeiqsEKTGmSyIvBHj1FqZiIpI")
    assert entry["size_bytes"] == 9174
    assert entry["sha256"] == EXPECTED_SHA256
    assert entry["github_paths"] == [
        "archive/authority-manifest/authority-v1.0.2-canon.json"
    ]
    assert entry["mirror_status"] == "repo_exact_hash_verified"
    assert registry["summary"]["semantic_correction_required"] == []
