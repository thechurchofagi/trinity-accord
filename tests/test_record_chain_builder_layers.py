from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "api" / "record-chain-builder-bundles.v1.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_builder_manifest_binds_all_three_execution_layers():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    canonical = data["canonical_builder"]
    assert canonical["architecture"] == "contract_entrypoint_recovery_wrapper_core_v1"

    layers = [
        (ROOT / "downloads" / "record-chain-builder.mjs", canonical),
        (
            ROOT / "downloads" / "record-chain-builder-recovery.mjs",
            canonical["recovery_wrapper"],
        ),
        (ROOT / "downloads" / "record-chain-builder-core.mjs", canonical["core"]),
    ]
    for path, contract in layers:
        assert path.is_file(), path
        assert path.stat().st_size == contract["size_bytes"]
        assert _sha256(path) == contract["sha256"]

    assert canonical["recovery_wrapper"]["read_only_recovery"] is True
    assert canonical["recovery_wrapper"]["maximum_submit_posts"] == 1
    assert canonical["core"]["must_match_sha256_and_size_before_execution"] is True
