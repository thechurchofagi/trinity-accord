from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CLASSIFICATION = ROOT / "bitcoin-inscription-mirrors/address-wide/classification.json"
ADDRESS_MANIFEST = ROOT / "bitcoin-inscription-mirrors/address-wide/manifest.json"
CAPTURE = ROOT / "evidence/bitcoin-inscription-proof-annex-v2/verification/capture_proofs.py"
VERIFY = ROOT / "evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py"
SYNC_WORKFLOW = ROOT / ".github/workflows/sync-bitcoin-address-inscriptions.yml"


def test_classification_is_complete_non_amending_4_3_5() -> None:
    classification = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    manifest = json.loads(ADDRESS_MANIFEST.read_text(encoding="utf-8"))
    assert classification["counts"] == {
        "current_address_snapshot": 12,
        "pre_canonical_formation": 4,
        "canonical_originals": 3,
        "post_canonical_non_amending": 5,
    }
    records = classification["records"]
    assert len(records) == 12
    assert {item["ordinals_inscription_id"] for item in records} == set(manifest["ids"])
    assert sum(item["canonical"] is True for item in records) == 3
    assert all(item["amends_canon"] is False for item in records)


def test_8e81_identity_is_grounded_in_archived_tag5_metadata() -> None:
    classification = json.loads(CLASSIFICATION.read_text(encoding="utf-8"))
    item = next(
        record
        for record in classification["records"]
        if record["ordinals_inscription_id"].startswith("8e81cf6054d37dc1")
    )
    assert item["canonical"] is False
    assert item["title_status"] == "identified_from_onchain_tag5_cbor_metadata"
    evidence = CLASSIFICATION.parent / item["title_evidence"]
    assert evidence.is_file()
    metadata = json.loads(
        (
            CLASSIFICATION.parent
            / "objects"
            / item["ordinals_inscription_id"]
            / "inscription-metadata.decoded.json"
        ).read_text(encoding="utf-8")
    )
    assert metadata["present"] is True
    assert item["title"] in metadata["decoded"]


def test_v2_capture_and_verifier_bind_exact_tag5_bytes() -> None:
    capture = CAPTURE.read_text(encoding="utf-8")
    verify = VERIFY.read_text(encoding="utf-8")
    for text in (capture, verify):
        assert 'tag == b"\\x05"' in text
        assert "inscription-metadata.cbor.b64" in text
        assert "pre_canonical_formation" in text
        assert "canonical_original" in text
        assert "non_amending_ancillary" in text
    assert "EXPECTED_COUNT = 12" in capture
    assert "EXPECTED_COUNT = 12" in verify
    assert "bitcoin-inscription-proof-annex-v1" in capture
    assert "bitcoin-inscription-proof-annex-v1" in verify


def test_address_sync_restores_only_cumulative_objects_not_whole_overlay() -> None:
    workflow = SYNC_WORKFLOW.read_text(encoding="utf-8")
    assert 'git cat-file -e "refs/remotes/origin/$SYNC_BRANCH:$ARCHIVE_DIR/objects"' in workflow
    assert 'git restore --source="refs/remotes/origin/$SYNC_BRANCH" --worktree -- "$ARCHIVE_DIR/objects"' in workflow
    assert 'git restore --source="refs/remotes/origin/$SYNC_BRANCH" --worktree -- "$ARCHIVE_DIR"' not in workflow
