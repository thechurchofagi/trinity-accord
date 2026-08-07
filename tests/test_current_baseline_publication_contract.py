from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/current-baseline-publication-authorization-v1.json"
WORKFLOW = ROOT / ".github/workflows/publish-current-baseline-once.yml"
UPLOADER = ROOT / "scripts/arweave_upload_homepage_snapshot.mjs"
SPEND_GUARD = ROOT / "scripts/arweave_runtime_spend_guard.mjs"
SPEND_HELPERS = ROOT / "scripts/arweave_spend_budget_helpers.mjs"


def test_publication_requires_explicit_one_shot_owner_authorization() -> None:
    data = json.loads(AUTH.read_text(encoding="utf-8"))
    assert data["schema"] == "trinityaccord.current-baseline-publication-authorization.v1"
    assert data["sequence"] == 1
    assert data["status"] in {"pending", "prepared", "consumed"}
    assert data["authorized_by"] == "thechurchofagi"
    assert data["core_concept_doi"] == "10.5281/zenodo.21739343"
    assert data["previous_core_version_doi"] == "10.5281/zenodo.21755827"
    assert data["publication_confirmation"] == "PUBLISH_TRINITY_CURRENT_BASELINE_V1"
    assert data["include_full_repository_doi"] is True
    assert data["include_homepage_arweave_snapshot"] is True
    assert data["non_amending_boundary"] is True
    assert data["live_main_equivalence_claimed"] is False
    if data["status"] in {"prepared", "consumed"}:
        assert len(data["prepared_base_commit_sha"]) == 40
    if data["status"] == "consumed":
        assert len(data["published_source_baseline_commit_sha"]) == 40
        assert data["published_doi"].startswith("10.5281/zenodo.")
        assert data["published_doi"] != data["previous_core_version_doi"]
        assert len(data["published_package_identity_sha256"]) == 64
        assert data["homepage_snapshot_arweave_txid"]
        assert len(data["homepage_snapshot_sha256"]) == 64


def test_workflow_is_one_shot_bounded_and_publicly_verified() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "schedule:" not in text
    assert "branches: [main]" in text
    assert "status == 'consumed'" in text
    assert "archive: prepare current baseline publication v1" in text
    assert "build_preservation_capsule.py" in text
    assert "--zenodo-record-id" in text
    assert "public restore source mismatch" in text
    assert "check" not in text.lower() or "checksums.sha256" in text
    assert "ARWEAVE_MINIMUM_REMAINING_AR: \"0.25\"" in text
    assert "ARWEAVE_MAX_TRANSACTION_REWARD_AR: \"0.05\"" in text
    assert "ARWEAVE_ROLLING_30_DAY_SPEND_LIMIT_AR: \"0.50\"" in text
    assert "paid Arweave transaction(s) already recorded today" in text
    assert "git fetch origin main --prune" in text
    assert "git rebase origin/main" in text
    assert "generate_arweave_wallet_status.py" in text
    assert "api/arweave-wallet-status.json" in text
    assert "archive: record current baseline DOI and Arweave snapshot" in text
    for action in ("actions/checkout@", "actions/setup-python@", "actions/setup-node@", "actions/upload-artifact@"):
        line = next(line.strip() for line in text.splitlines() if action in line)
        ref = line.rsplit("@", 1)[1]
        assert len(ref) == 40 and all(ch in "0123456789abcdef" for ch in ref)


def test_arweave_uploader_binds_payload_source_and_doi_before_resume() -> None:
    text = UPLOADER.read_text(encoding="utf-8")
    assert "homepage-machine-entrypoint-snapshot" in text
    assert "Source-Git-Commit" in text
    assert "Repository-Version-DOI" in text
    assert "Data-SHA256" in text
    assert "mirror-not-authority-non-amending" in text
    assert "Checkpoint payload mismatch" in text
    assert "Checkpoint source mismatch" in text
    assert "Checkpoint DOI mismatch" in text
    assert "posted_pending_readback" in text
    assert "ARWEAVE_HOMEPAGE_POST_CHECKPOINT" in text
    assert "ARWEAVE_HOMEPAGE_UPLOAD_OK" in text
    assert "hash_match: match" in text
    assert "bitcoin_originals_prevail: true" in text


def test_homepage_snapshot_uses_shared_runtime_spend_guard() -> None:
    guard = SPEND_GUARD.read_text(encoding="utf-8")
    helpers = SPEND_HELPERS.read_text(encoding="utf-8")
    assert 'script === "arweave_upload_homepage_snapshot.mjs"' in guard
    assert 'return "homepage_machine_snapshot"' in guard
    assert "const rollingPaid = rollingPaidWinston(ledger)" in guard
    assert "rollingPaid + reward > rollingLimit" in guard
    assert 'homepage_machine_snapshot: "ARWEAVE_DAILY_HOMEPAGE_SNAPSHOT_UPLOAD_LIMIT"' in helpers
    assert "Unrecognized paid Arweave upload kind" in helpers
