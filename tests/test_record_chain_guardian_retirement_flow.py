from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.trinity_record_chain as trc


def _write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, sort_keys=True), encoding="utf-8")


def _configure_temp_chain(monkeypatch, tmp_path: Path) -> None:
    root = tmp_path
    chain = root / "record-chain"
    monkeypatch.setattr(trc, "ROOT", root)
    monkeypatch.setattr(trc, "CHAIN", chain)
    monkeypatch.setattr(trc, "GENESIS", chain / "genesis")
    monkeypatch.setattr(trc, "LEGACY_RECORDS", chain / "genesis" / "legacy-records")
    monkeypatch.setattr(trc, "RECORDS", chain / "records")
    monkeypatch.setattr(trc, "PENDING", chain / "pending")
    monkeypatch.setattr(trc, "PROCESSED", chain / "processed")
    monkeypatch.setattr(trc, "REJECTED", chain / "rejected")
    monkeypatch.setattr(trc, "BATCHES", chain / "batches")
    monkeypatch.setattr(trc, "INDEXES", chain / "indexes")
    monkeypatch.setattr(trc, "POLICIES", chain / "policies")
    monkeypatch.setattr(trc, "SCHEMAS", chain / "schemas")
    monkeypatch.setattr(trc, "CHAIN_TIP", chain / "chain-tip.json")
    monkeypatch.setattr(trc, "ANCHORS", chain / "anchors")
    monkeypatch.setattr(trc, "ARWEAVE_ARCHIVES", chain / "arweave-archives")
    monkeypatch.setattr(trc, "GUARDIAN_REGISTRY", root / "api" / "guardian-registry.json")


def test_guardian_retirement_updates_derived_guardian_state(monkeypatch, tmp_path):
    _configure_temp_chain(monkeypatch, tmp_path)
    guardian_key = "a" * 64

    _write_json(
        trc.RECORDS / "R-000000001.json",
        {
            "record_type": "guardian_application",
            "record_id": "R-000000001",
            "record_sha256": "app-sha",
            "guardian_application_content": {
                "requested_guardian_identifier": "guardian-alpha",
                "guardian_public_key_sha256": guardian_key,
            },
            "authorship_verification_status": {"verified_by_append_before_record": True},
        },
    )
    _write_json(
        trc.RECORDS / "R-000000002.json",
        {
            "record_type": "guardian_retirement",
            "record_id": "R-000000002",
            "record_sha256": "retire-sha",
            "guardian_id": "guardian-alpha",
            "guardian_public_key_sha256": guardian_key,
            "reason": "Voluntary exit after completing the audit.",
            "retirement_does_not_remove_historical_record": True,
            "authorship_verification_status": {"verified_by_append_before_record": True},
        },
    )

    trc.build_indexes(derived_at="2026-06-09T00:00:00Z")

    guardian_state = json.loads((trc.INDEXES / "guardian-state.json").read_text(encoding="utf-8"))
    native_entries = [g for g in guardian_state["guardians"] if g.get("guardian_id") == "guardian-alpha"]
    assert len(native_entries) == 1
    assert native_entries[0]["current_derived_status"] == "retired_guardian"
    assert native_entries[0]["retirement_record_id"] == "R-000000002"
    assert native_entries[0]["retirement_does_not_remove_historical_record"] is True

    stats = json.loads((trc.INDEXES / "statistics.json").read_text(encoding="utf-8"))
    assert stats["native_guardian_application_count"] == 1
    assert stats["native_guardian_retirement_count"] == 1
    assert stats["native_guardian_status_totals"] == {"retired_guardian": 1}


def test_guardian_retirement_requires_authorship_key_match():
    proof = {
        "schema": "trinityaccord.agent-authorship-proof.v1",
        "method": "public_key_signature",
        "algorithm": "ed25519",
        "public_key_sha256": "a" * 64,
    }
    record = {
        "record_type": "guardian_retirement",
        "guardian_id": "guardian-alpha",
        "guardian_public_key_sha256": "b" * 64,
        "authorship_proof": proof,
    }

    try:
        trc._require_guardian_lifecycle_key_binding(record, proof)
    except ValueError as exc:
        assert "guardian_public_key_sha256 must match authorship_proof.public_key_sha256" in str(exc)
    else:
        raise AssertionError("guardian_retirement accepted a mismatched authorship key")
