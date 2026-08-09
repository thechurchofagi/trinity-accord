from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCOPE = ROOT / "api/ethereum-address-evidence-scope.v1.json"
ANNEX = ROOT / "evidence/ethereum-evidence-annex-v1/ANNEX-MANIFEST.json"


def digest(value: dict) -> str:
    material = dict(value)
    material.pop("source_digest", None)
    raw = json.dumps(
        material, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def test_address_scope_partition_is_explicit_observation_bounded_and_complete():
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    annex = json.loads(ANNEX.read_text(encoding="utf-8"))
    assert scope["schema"] == "trinityaccord.ethereum-address-evidence-scope.v1"
    assert scope["status"] == "PASS"
    assert scope["source_digest"] == digest(scope)
    assert "not a cryptographic proof" in scope["observation_boundary"]
    summary = scope["summary"]
    assert summary == {
        "observed_transactions": 232,
        "outgoing_transactions": 220,
        "incoming_transactions": 12,
        "outgoing_nonce_min": 0,
        "outgoing_nonce_max": 219,
        "outgoing_nonces_contiguous": True,
        "non_nft_evidence_self_transactions": 12,
        "chronicle_nft_mint_transactions": 175,
        "other_outgoing_account_operations": 33,
        "max_observed_block": 25377890,
    }
    records = scope["non_nft_evidence"]["records"]
    assert {item["tx_hash"] for item in records} == {
        item["tx_hash"] for item in annex["anchors"]
    }
    assert len(scope["other_outgoing_account_operations"]) == 33
    assert len(scope["incoming_transactions"]) == 12


def test_address_scope_keeps_frozen_doi_separate_from_live_post_freeze_delta():
    scope = json.loads(SCOPE.read_text(encoding="utf-8"))
    freeze = scope["freeze_boundary"]
    assert freeze["published_final_doi_v3"] == "10.5281/zenodo.21855814"
    assert freeze["published_final_doi_v3_non_nft_anchor_count"] == 10
    assert freeze["current_live_repository_non_nft_anchor_count"] == 12
    assert set(freeze["post_freeze_addition_tx_hashes"]) == {
        "0x06b1d82b7828054f249cdcc2e820321f634bd8bef44318751113098d2ee37acd",
        "0x04314e8f9b47fac54dcf2db3a65f40aad60c226e65614f0ad22588bd39c416d2",
    }
    auth = json.loads(
        (
            ROOT
            / "preservation/current-baseline-publication-authorization-v4.json"
        ).read_text(encoding="utf-8")
    )
    expected = {
        "pending": "owner_authorized_pending_publication_v4",
        "prepared": "prepared_for_publication_v4",
        "consumed": "published_verified_and_consumed",
    }[auth["status"]]
    assert freeze["new_doi_publication_status"] == expected
    assert freeze["new_arweave_upload_status"] in {
        "intentionally_deferred_not_authorized",
        "intentionally_deferred_not_attempted",
    }
    assert freeze["current_checkpoint_v4_includes_post_freeze_additions"] is (
        auth["status"] == "consumed"
    )
