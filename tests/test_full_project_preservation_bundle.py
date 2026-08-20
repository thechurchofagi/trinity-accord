from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from scripts import verify_full_project_preservation_bundle as verifier


def _write_minimal_bundle(root: Path) -> dict:
    payload = b"trinity-preservation-test\n"
    sha = hashlib.sha256(payload).hexdigest()
    object_path = root / "objects" / "sha256" / sha[:2] / sha
    object_path.parent.mkdir(parents=True, exist_ok=True)
    object_path.write_bytes(payload)
    manifest = {
        "schema": verifier.SCHEMA,
        "generated_at_utc": "test-only",
        "source_repository": "thechurchofagi/trinity-accord",
        "source_git_commit_sha": "a" * 40,
        "source_git_tree_oid": "b" * 40,
        "authority_boundary": {
            "canonical_interpretive_authority": "three_bitcoin_originals_only",
            "ethereum_chronicle_status": "175_entry_corpus_unchanged",
            "crosschain_record_status": "noncanonical_historical_evidence_and_formation_context_only",
            "non_amending_preservation": True,
        },
        "known_limitations": {
            "sidechain_historical_payload_unresolved_roots": 7,
            "sidechain_exact_car_roots": 250,
            "sidechain_total_ipfs_roots": 257,
            "external_dataverse_copy_created": False,
        },
        "sources": [
            {
                "source_id": "test",
                "kind": "test",
                "files": [
                    {
                        "logical_path": "source/example.bin",
                        "object_sha256": sha,
                        "bytes": len(payload),
                    }
                ],
            }
        ],
        "objects": [{"sha256": sha, "bytes": len(payload), "origin_count": 1}],
    }
    manifest["bundle_identity_sha256"] = hashlib.sha256(
        verifier.canonical_identity_material(manifest)
    ).hexdigest()
    (root / "full-project-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return manifest


def test_minimal_bundle_verifies_and_materializes(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = _write_minimal_bundle(bundle)
    restored = tmp_path / "restored"
    report = verifier.verify_bundle(bundle, restored)
    assert report["result"] == "pass"
    assert report["bundle_identity_sha256"] == manifest["bundle_identity_sha256"]
    assert report["unique_object_count"] == 1
    assert (restored / "source" / "example.bin").read_bytes() == b"trinity-preservation-test\n"


def test_tampered_object_is_rejected(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = _write_minimal_bundle(bundle)
    sha = manifest["objects"][0]["sha256"]
    path = bundle / "objects" / "sha256" / sha[:2] / sha
    path.write_bytes(b"tampered\n")
    with pytest.raises(SystemExit, match="object size mismatch|object hash mismatch"):
        verifier.verify_bundle(bundle)


def test_authority_boundary_is_fail_closed(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    bundle.mkdir()
    manifest = _write_minimal_bundle(bundle)
    manifest["authority_boundary"]["canonical_interpretive_authority"] = "expanded"
    manifest["bundle_identity_sha256"] = hashlib.sha256(
        verifier.canonical_identity_material(manifest)
    ).hexdigest()
    (bundle / "full-project-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    with pytest.raises(SystemExit, match="canonical authority boundary changed"):
        verifier.verify_bundle(bundle)
