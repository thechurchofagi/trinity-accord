from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RECONCILIATION = ROOT / "preservation/current-baseline-publication-reconciliation-v1.json"
WORKFLOW = ROOT / ".github/workflows/reconcile-current-baseline-publication.yml"
ARTIFACT_VALIDATOR = ROOT / "scripts/validate_current_baseline_reconciliation_artifact.py"
READBACK = ROOT / "scripts/verify_arweave_existing_payload.mjs"
FINALIZER = ROOT / "scripts/finalize_current_baseline_reconciliation.py"
WALLET_LEDGER_TEST = ROOT / "scripts/test_arweave_wallet_ledger_update.py"
DOWNLOAD_ARTIFACT_SHA = "3e5f45b2cfb9172054b4087a40e8e0b5a5461e7c"


def test_reconciliation_is_exact_owner_authorized_and_read_only() -> None:
    data = json.loads(RECONCILIATION.read_text(encoding="utf-8"))
    assert data["schema"] == "trinityaccord.current-baseline-publication-reconciliation.v1"
    assert data["sequence"] == 1
    assert data["status"] in {"pending", "consumed"}
    assert data["authorized_by"] == "thechurchofagi"
    assert data["source_git_commit_sha"] == "3e013bbb44a741546db68013c4034c2121017f33"
    assert data["zenodo_record_id"] == 21831412
    assert data["version_doi"] == "10.5281/zenodo.21831412"
    assert data["concept_doi"] == "10.5281/zenodo.21739343"
    assert data["package_identity_sha256"] == "1630e44bdec257c0c3278c79ab2eb4a6787cc7ac861e34e8dc470b63cf091b54"
    assert data["arweave_txid"] == "-lAi9yvTzgfDTx32n8nzNRKAGOegO_croyzNHX3y7IM"
    assert data["arweave_payload_sha256"] == "361f0a1479e48fc5b194f19a65929a1dad53c1264a593e163eb24b3cacc8be63"
    assert data["arweave_payload_bytes"] == 51342
    assert data["failed_workflow_run_id"] == 31143394148
    assert data["proof_artifact_id"] == 8980674728
    assert data["external_writes_already_complete"] is True
    assert data["allow_zenodo_write"] is False
    assert data["allow_arweave_post"] is False
    assert data["non_amending_boundary"] is True
    assert data["live_main_equivalence_claimed"] is False


def test_reconciliation_workflow_reverifies_without_external_write_paths() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "schedule:" not in text
    assert "actions: read" in text and "contents: write" in text
    assert f"actions/download-artifact@{DOWNLOAD_ARTIFACT_SHA}" in text
    assert "python3 -m pip install -r requirements-ci.txt" in text
    assert "validate_current_baseline_reconciliation_artifact.py" in text
    assert "repository_preservation_refresh.py verify-public" in text
    assert "verify_arweave_existing_payload.mjs" in text
    assert "finalize_current_baseline_reconciliation.py" in text
    assert "validate_current_baseline_publication_state.py" in text
    assert "python3 scripts/test_arweave_wallet_ledger_update.py" in text
    assert WALLET_LEDGER_TEST.is_file()
    assert "tests/test_arweave_wallet_ledger.py" not in text
    assert "publish_preservation_capsule_to_zenodo" not in text
    assert "arweave_upload_homepage_snapshot.mjs" not in text
    assert "ZENODO_ACCESS_TOKEN" not in text
    assert "ARKEY" not in text
    assert "archive: reconcile current baseline DOI and Arweave snapshot" in text
    for action in (
        "actions/checkout@",
        "actions/setup-python@",
        "actions/setup-node@",
        "actions/download-artifact@",
        "actions/upload-artifact@",
    ):
        line = next(line.strip() for line in text.splitlines() if action in line)
        ref = line.rsplit("@", 1)[1]
        assert len(ref) == 40 and all(ch in "0123456789abcdef" for ch in ref)


def test_retained_artifact_validator_binds_every_external_identity() -> None:
    text = ARTIFACT_VALIDATOR.read_text(encoding="utf-8")
    assert 'authorization.get("allow_zenodo_write") is not False' in text
    assert 'authorization.get("allow_arweave_post") is not False' in text
    assert 'work.get("latest_package_identity_sha256") == package' in text
    assert 'receipt.get("readback_sha256") == expected_payload' in text
    assert "unsafe snapshot member" in text
    assert "snapshot file differs from exact source" in text
    assert "snapshot checksum mismatch" in text


def test_arweave_reconciliation_verifier_has_no_posting_capability() -> None:
    text = READBACK.read_text(encoding="utf-8")
    assert "transactions.getData" in text
    assert "transactions.get(txid)" in text
    assert "Source-Git-Commit" in text
    assert "Repository-Version-DOI" in text
    assert "Data-SHA256" in text
    assert "ARWEAVE_EXISTING_PAYLOAD_VERIFIED" in text
    for forbidden in ("createTransaction", "transactions.sign", "transactions.post", "ARKEY"):
        assert forbidden not in text


def test_finalizer_requires_public_doi_and_arweave_proofs() -> None:
    text = FINALIZER.read_text(encoding="utf-8")
    assert 'reconciliation.get("allow_zenodo_write") is False' in text
    assert 'reconciliation.get("allow_arweave_post") is False' in text
    assert 'metadata.get("observed_without_zenodo_credentials") is True' in text
    assert 'recovery.get("package_identity_sha256") == package' in text
    assert 'arweave.get("readback_sha256") == payload_sha' in text
    assert '"reconciliation_performed_no_external_write": True' in text
    assert '"previous_verified_version": previous' in text
