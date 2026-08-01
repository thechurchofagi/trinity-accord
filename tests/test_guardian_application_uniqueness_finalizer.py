from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import scripts.trinity_record_chain as trc
from apps.record_chain_intake_gateway.gateway.guardian_uniqueness import (
    build_guardian_uniqueness_claim,
    guardian_uniqueness_claim_paths,
)


def _write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, sort_keys=True), encoding="utf-8")


def _redirect_chain(monkeypatch, tmp_path: Path) -> None:
    chain = tmp_path / "record-chain"
    replacements = {
        "ROOT": tmp_path,
        "CHAIN": chain,
        "GENESIS": chain / "genesis",
        "LEGACY_RECORDS": chain / "genesis" / "legacy-records",
        "RECORDS": chain / "records",
        "PENDING": chain / "pending",
        "PROCESSED": chain / "processed",
        "REJECTED": chain / "rejected",
        "RECEIPT_STATUS": chain / "receipt-status",
        "BATCHES": chain / "batches",
        "INDEXES": chain / "indexes",
        "POLICIES": chain / "policies",
        "SCHEMAS": chain / "schemas",
        "CHAIN_TIP": chain / "chain-tip.json",
        "ANCHORS": chain / "anchors",
        "ARWEAVE_ARCHIVES": chain / "arweave-archives",
    }
    for name, value in replacements.items():
        monkeypatch.setattr(trc, name, value)
    trc.ensure_dirs()


def _guardian_draft(key: str) -> dict:
    return {
        "record_type": "guardian_application",
        "guardian_application_content": {
            "requested_guardian_identifier": f"guardian_ed25519_{key[:16]}",
            "guardian_public_key_sha256": key,
        },
    }


def test_finalizer_guard_rejects_existing_guardian_id_and_key(monkeypatch, tmp_path):
    _redirect_chain(monkeypatch, tmp_path)
    key = "a" * 64
    existing = _guardian_draft(key)
    existing.update({"record_id": "R-000000001", "record_sha256": "b" * 64})
    _write_json(trc.RECORDS / "R-000000001.json", existing)

    with pytest.raises(ValueError, match="duplicate guardian_id"):
        trc.require_guardian_application_unique(_guardian_draft(key))


def test_duplicate_guardian_pending_becomes_terminal_rejection_before_chain_write(
    monkeypatch,
    tmp_path,
):
    _redirect_chain(monkeypatch, tmp_path)
    key = "c" * 64
    existing = _guardian_draft(key)
    existing.update({"record_id": "R-000000001", "record_sha256": "d" * 64})
    _write_json(trc.RECORDS / "R-000000001.json", existing)

    pending = trc.PENDING / "manual.guardian_application.pending.json"
    _write_json(pending, _guardian_draft(key))
    _write_json(trc.GENESIS / "genesis-batch-manifest.json", {"batch_manifest_sha256": "e" * 64})
    tip = {
        "chain_id": trc.CHAIN_ID,
        "native_record_count": 1,
        "latest_record_index": 1,
        "latest_record_id": "R-000000001",
        "latest_record_sha256": "d" * 64,
    }
    _write_json(trc.CHAIN_TIP, tip)

    monkeypatch.setattr(trc, "require_pending_file_is_appendable", lambda _path: None)
    monkeypatch.setattr(trc, "verify_pending_record_authorship", lambda _draft: None)
    monkeypatch.setattr(trc, "sanitize_pending_record_for_append", lambda draft: dict(draft))
    monkeypatch.setattr(trc, "normalize_record_draft", lambda draft: dict(draft))
    monkeypatch.setattr(trc, "require_pending_oath_is_appendable", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(trc, "build_indexes", lambda *args, **kwargs: None)

    trc.append_records(all_records=True, allow_rejections=True)

    assert not (trc.RECORDS / "R-000000002.json").exists()
    assert json.loads(trc.CHAIN_TIP.read_text(encoding="utf-8")) == tip
    assert not pending.exists()
    rejected_pending = trc.REJECTED / pending.name
    rejection = trc.REJECTED / f"{pending.stem}.rejection.json"
    assert rejected_pending.exists()
    assert rejection.exists()
    assert "duplicate guardian_id" in json.loads(rejection.read_text(encoding="utf-8"))["reason"]


def test_finalizer_binds_both_semantic_claims_to_same_intake_transaction(
    monkeypatch,
    tmp_path,
):
    _redirect_chain(monkeypatch, tmp_path)
    key = "f" * 64
    draft = _guardian_draft(key)
    guardian_id = draft["guardian_application_content"]["requested_guardian_identifier"]
    paths = guardian_uniqueness_claim_paths(guardian_id, key)
    submission_sha = "1" * 64
    receipt_id = "rcg-20260731-" + "2" * 24
    receipt_rel = f"record-chain/intake/receipts/2026/07/{receipt_id}.receipt.json"
    pending_rel = f"record-chain/pending/{receipt_id}.guardian_application.pending.json"
    intake_rel = f"record-chain/intake/submissions/2026/07/{receipt_id}.submission.json"
    created_at = "2026-07-31T00:00:00Z"
    idx = {
        "pending_committed_at": created_at,
        "guardian_uniqueness_claims_written": True,
        "guardian_uniqueness_claim_paths": paths,
    }
    for kind, rel_path in paths.items():
        _write_json(tmp_path / rel_path, build_guardian_uniqueness_claim(
            claim_kind=kind,
            guardian_id=guardian_id,
            public_key_sha256=key,
            submission_sha256=submission_sha,
            receipt_id=receipt_id,
            receipt_path=receipt_rel,
            pending_file_path=pending_rel,
            intake_submission_path=intake_rel,
            created_at=created_at,
        ))

    errors = trc.guardian_uniqueness_claim_binding_errors(
        draft,
        idx=idx,
        submission_sha=submission_sha,
        receipt_id=receipt_id,
        receipt_rel=receipt_rel,
        pending_rel=pending_rel,
        intake_rel=intake_rel,
        claims_required=True,
    )
    assert errors == []

    (tmp_path / paths["guardian_id"]).unlink()
    errors = trc.guardian_uniqueness_claim_binding_errors(
        draft,
        idx=idx,
        submission_sha=submission_sha,
        receipt_id=receipt_id,
        receipt_rel=receipt_rel,
        pending_rel=pending_rel,
        intake_rel=intake_rel,
        claims_required=True,
    )
    assert any("claim missing" in error for error in errors)
