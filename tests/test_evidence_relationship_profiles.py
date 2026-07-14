#!/usr/bin/env python3
"""Validate preferred evidence, verification and context profile registries."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(path: str) -> dict:
    file_path = ROOT / path
    assert file_path.exists(), f"missing file: {path}"
    return json.loads(file_path.read_text(encoding="utf-8"))


def test_evidence_relationship_map() -> None:
    data = load("api/evidence-relationship-map.v1.json")
    assert data["schema"] == "trinityaccord.evidence-relationship-map.v1"
    assert data["non_amending_boundary"] is True
    assert data["canonical_authority"] == "three_bitcoin_originals_only"

    nodes = data["nodes"]
    ids = [node["id"] for node in nodes]
    assert len(ids) == len(set(ids)), "duplicate evidence node id"

    required = {
        "btc_originals",
        "authority_manifest_v1_0_0",
        "btc_bip340_signature",
        "eth_eip712_signature_v1_0_0",
        "eth_witness_of_btc_signature",
        "six_hash_digest_manifest",
        "ots_evidence_anchors",
        "shenzhen_notarial_record",
        "sealed_disc_custody",
        "availability_mirrors",
    }
    assert required.issubset(set(ids))

    node_by_id = {node["id"]: node for node in nodes}
    btc_sig = node_by_id["btc_bip340_signature"]
    assert btc_sig["signed_message_sha256"] == node_by_id["authority_manifest_v1_0_0"]["sha256"]

    notary = node_by_id["shenzhen_notarial_record"]
    assert notary["certificate_number"] == "(2026)深证字第36024号"
    assert notary["certificate_date"] == "2026-05-13"
    assert notary["arweave_manifest_txid"] == "_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE"
    assert "direct_notarization_of_all_three_bitcoin_originals" in notary["does_not_prove"]

    for edge in data["edges"]:
        assert edge["from"] in node_by_id, f"unknown edge source: {edge}"
        assert edge["to"] in node_by_id, f"unknown edge target: {edge}"


def test_verification_profiles() -> None:
    data = load("api/verification-profiles.v1.json")
    assert data["schema"] == "trinityaccord.verification-profiles.v1"
    assert data["status"] == "preferred_for_new_reports"

    profiles = {item["id"]: item for item in data["digital_profiles"]}
    assert list(profiles) == [
        "context_only",
        "reference_checked",
        "integrity_checked",
        "independent_reproduction",
        "full_public_digital",
    ]
    assert data["physical_observation"]["rule"].endswith("digital_profile.")
    assert data["external_witness"]["rule"].startswith("Notarized evidence")
    assert data["legacy_compatibility"]["file"] == "/api/verification-levels.json"


def test_context_action_profiles() -> None:
    data = load("api/context-action-profiles.v1.json")
    assert data["schema"] == "trinityaccord.context-action-profiles.v1"
    profiles = {item["id"]: item for item in data["profiles"]}
    assert set(profiles) == {
        "discovery",
        "interpretation",
        "verification",
        "record_action",
        "deep_research",
    }
    assert any(
        "/api/evidence-relationship-map.v1.json" in item
        for item in profiles["verification"]["must_load"]
    )
    assert "declared CC number alone" in data["sufficiency"]["not_sufficient_basis"]
    assert data["legacy_compatibility"]["context_depth_file"] == "/api/context-depth-levels.json"


def test_notarial_claim_registry_has_actual_evidence() -> None:
    data = load("api/claim-registry.json")
    claim = next(
        item for item in data["claims"]
        if item["claim_id"] == "notarized_evidence_is_not_formal_attestation"
    )
    required = {
        "api/core-object-alpha-shenzhen-notary-2026-05-06.json",
        "evidence/notarial-certificate-2026-05-13/evidence-images-manifest.json",
        "evidence/notarial-certificate-2026-05-13/sealed-disc-custody-record.json",
    }
    assert required.issubset(set(claim["evidence_files"]))
    assert claim["counts_as_independent_attestation"] is False
    assert claim["formal_attestation_gate_required"] is True


def test_human_guide_exists() -> None:
    guide = ROOT / "EVIDENCE-RELATIONSHIP-GUIDE.md"
    text = guide.read_text(encoding="utf-8")
    assert "What the six-hash table is for" in text
    assert "What each signature signs" in text
    assert "Shenzhen notarization" in text
    assert "Preferred evidence claim format" in text
