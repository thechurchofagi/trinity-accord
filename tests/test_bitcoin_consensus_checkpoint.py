from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "bitcoin_consensus_checkpoint.py"
SPEC = importlib.util.spec_from_file_location("bitcoin_consensus_checkpoint", MODULE_PATH)
assert SPEC and SPEC.loader
checkpoint = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checkpoint)


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


def valid_manifest(sequence: int = 1) -> dict:
    previous = None
    if sequence > 1:
        previous = {
            "tag": f"bitcoin-consensus-checkpoint-{sequence - 1:06d}",
            "manifest_sha256": _sha("previous"),
        }
    return {
        "schema": checkpoint.SCHEMA,
        "profile": checkpoint.PROFILE,
        "network": "main",
        "bitcoin_core_version": "31.1",
        "bitcoin_core_archive_sha256": _sha("bitcoin-core"),
        "assumevalid": "0",
        "prune_mib": 550,
        "clean_shutdown": True,
        "initialblockdownload": True,
        "height": 500000,
        "best_block_hash": _sha("block"),
        "verification_progress": 0.75,
        "workflow": {
            "repository": "thechurchofagi/trinity-accord",
            "run_id": "123",
            "run_attempt": "1",
            "sha": "a" * 40,
        },
        "checkpoint": {
            "sequence": sequence,
            "tag": f"bitcoin-consensus-checkpoint-{sequence:06d}",
            "created_at": "2026-08-31T12:00:00Z",
        },
        "previous_checkpoint": previous,
        "assets": [
            {
                "name": "bitcoin-datadir.tar.zst.part-0000",
                "size": 10,
                "sha256": _sha("asset"),
            }
        ],
    }


def test_accepts_genesis_checkpoint_manifest():
    checkpoint.validate_manifest(valid_manifest())


def test_accepts_linked_successor_manifest():
    checkpoint.validate_manifest(valid_manifest(2))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("assumevalid", "0000000000000000000000000000000000000000000000000000000000000000"),
        ("clean_shutdown", False),
        ("network", "test"),
        ("profile", "dual_remote_esplora"),
    ],
)
def test_rejects_trust_boundary_downgrades(field, value):
    manifest = valid_manifest()
    manifest[field] = value
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.validate_manifest(manifest)


def test_rejects_broken_predecessor_chain():
    manifest = valid_manifest(3)
    manifest["previous_checkpoint"]["tag"] = "bitcoin-consensus-checkpoint-000001"
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.validate_manifest(manifest)


def test_rejects_duplicate_assets():
    manifest = valid_manifest()
    manifest["assets"].append(dict(manifest["assets"][0]))
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.validate_manifest(manifest)


def test_verify_asset_checks_size_and_sha256(tmp_path: Path):
    payload = b"checkpoint-part"
    path = tmp_path / "bitcoin-datadir.tar.zst.part-0000"
    path.write_bytes(payload)
    manifest = valid_manifest()
    manifest["assets"][0]["size"] = len(payload)
    manifest["assets"][0]["sha256"] = hashlib.sha256(payload).hexdigest()

    checkpoint.verify_asset(manifest, path.name, path)

    path.write_bytes(payload + b"corrupt")
    with pytest.raises(checkpoint.CheckpointError):
        checkpoint.verify_asset(manifest, path.name, path)


def test_canonical_manifest_serialization_is_stable(tmp_path: Path):
    manifest = valid_manifest()
    first = tmp_path / "one.json"
    second = tmp_path / "two.json"
    checkpoint.write_canonical_json(manifest, first)
    checkpoint.write_canonical_json(json.loads(first.read_text()), second)
    assert first.read_bytes() == second.read_bytes()
    assert checkpoint.sha256_file(first) == checkpoint.sha256_file(second)
