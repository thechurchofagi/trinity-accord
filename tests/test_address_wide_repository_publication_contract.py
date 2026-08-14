from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/address-wide-repository-publication-authorization-v1.json"
MANIFEST = ROOT / "bitcoin-inscription-mirrors/address-wide/manifest.json"
CLASSIFICATION = ROOT / "bitcoin-inscription-mirrors/address-wide/classification.json"
WORKFLOW = ROOT / ".github/workflows/publish-address-wide-repository-preservation.yml"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_authorization_is_one_shot_non_amending_and_exact_scope() -> None:
    auth = load(AUTH)
    assert auth["schema"] == "trinityaccord.address-wide-repository-publication-authorization.v1"
    assert auth["sequence"] == 1
    assert auth["status"] in {"pending", "consumed"}
    assert auth["authorized_by"] == "thechurchofagi"
    assert auth["core_concept_doi"] == "10.5281/zenodo.21739343"
    assert auth["previous_core_version_doi"] == "10.5281/zenodo.21859437"
    assert auth["publication_confirmation"] == "PUBLISH_TRINITY_ADDRESS_WIDE_REPOSITORY_V1"
    assert auth["required_address_archive_commit_sha"] == "3c3070dc799d2dcff16aef95e95d3b65f1c7d1bd"
    assert auth["include_full_repository_doi"] is True
    assert auth["include_arweave_upload"] is False
    assert auth["non_amending_boundary"] is True
    assert auth["three_bitcoin_originals_remain_canonical"] is True
    assert auth["live_main_equivalence_claimed"] is False
    assert auth["future_material_versions_allowed"] is True
    assert auth["address_archive_scope"] == {
        "authority_address": "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf",
        "current_address_snapshot": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
        "exact_content_bytes_archived": True,
        "recursive_ord_metadata_archived": True,
        "decoded_content_sha256_archived": True,
        "exact_content_length_archived": True,
    }
    proof = auth["proof_boundary"]
    assert proof["curated_l1_l2_l3_annex_inscriptions"] == 8
    assert proof["recovered_formation_records_with_l1_l2_l3_parity"] == 0


def test_address_archive_and_classification_are_complete_and_bounded() -> None:
    manifest = load(MANIFEST)
    classification = load(CLASSIFICATION)
    assert manifest["count"] == 12
    assert len(manifest["ids"]) == 12
    assert len(set(manifest["ids"])) == 12
    assert len(manifest["objects"]) == 12
    assert manifest["authority_boundary"] == {
        "archive_only": True,
        "same_address_does_not_imply_canonical": True,
        "three_bitcoin_originals_remain_canonical": True,
    }
    counts = classification["counts"]
    assert counts == {
        "current_address_snapshot": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
    }
    records = classification["records"]
    assert len(records) == 12
    assert {record["ordinals_inscription_id"] for record in records} == set(manifest["ids"])
    assert sum(record["canonical"] is True for record in records) == 3
    assert all(record["amends_canon"] is False for record in records)
    proto = next(record for record in records if record["role"] == "direct_proto_protocol")
    assert proto["canonical"] is False
    assert proto["ordinals_inscription_id"] == "138da690affc0f3595a7cebfd152a9715f3b0ca1a5baab93069e8c5c51a82f10i0"


def test_workflow_reuses_repository_preservation_primitives_without_arweave() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "build_preservation_capsule.py" in text
    assert "publish_preservation_capsule_to_zenodo_v3.py" in text
    assert "repository_preservation_refresh.py verify-public" in text
    assert "--zenodo-record-id" in text
    assert "toolchain_provenance.py" in text
    assert "PUBLISH_TRINITY_ADDRESS_WIDE_REPOSITORY_V1" in text
    assert "thechurchofagi" in text
    assert "arweave" not in text.lower()
