from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/repository-preservation-refresh-authorization.json"
CATALOG = ROOT / "preservation/recovery-catalog.json"
STATE = ROOT / "preservation/repository-preservation-state-v2.json"
OBSERVATION = ROOT / "preservation/repository-preservation-observation.json"
WORKFLOW = ROOT / ".github/workflows/repository-preservation-refresh.yml"
CONTROLLER = ROOT / ".github/workflows/repository-preservation-capsule.yml"
INTEGRITY = ROOT / ".github/workflows/repository-integrity.yml"
RUNNER = ROOT / "scripts/run_repository_preservation_refresh_ci.sh"
SCRIPT = ROOT / "scripts/repository_preservation_refresh.py"


def load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def test_refresh_contract_validates_in_pending_prepared_and_final_states():
    subprocess.run([sys.executable, str(SCRIPT), "validate"], cwd=ROOT, check=True)


def test_recovery_catalog_is_stable_and_github_independent():
    catalog = load(CATALOG)
    assert catalog["schema"] == "trinityaccord.repository-recovery-catalog.v1"
    core = catalog["core_repository"]
    assert core["concept_doi"] == "10.5281/zenodo.21739343"
    assert core["resolution_rule"] == (
        "Resolve the concept DOI and select its latest published version."
    )
    assert "moving GitHub main" in core["coverage_rule"]
    annexes = catalog["external_binary_annexes"]
    assert annexes["evidence"]["doi"] == "10.5281/zenodo.21753937"
    assert annexes["nft"]["doi"] == "10.5281/zenodo.21754229"
    assert catalog["github_required_for_discovery"] is False
    assert catalog["github_required_for_recovery"] is False


def test_refresh_authorization_is_exact_and_non_amending():
    auth = load(AUTH)
    assert auth["schema"] == (
        "trinityaccord.repository-preservation-refresh-authorization.v1"
    )
    assert auth["sequence"] == 3
    assert auth["authorized_by"] == "thechurchofagi"
    assert auth["rights_boundary_acknowledgement"] == (
        "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"
    )
    assert auth["publication_confirmation"] == (
        "PUBLISH_TRINITY_REPOSITORY_CAPSULE_REFRESH_V3"
    )
    assert auth["live_main_equivalence_claimed"] is False
    assert auth["non_amending_boundary"] is True


def test_manual_refresh_workflow_retains_safe_exact_source_publication_path():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "workflow_dispatch:" in text
    assert "group: main-write-lock" in text
    assert "queue: max" in text
    assert "repository-preservation-refresh-authorization.json" in text
    assert "archive: prepare repository preservation refresh v2" in text
    assert "--commit \"${{ steps.prepare.outputs.source_sha }}\"" in text
    assert "--state preservation/repository-preservation-state-v2.json" in text
    assert "Prove local GitHub-zero recovery before publication" in text
    assert "Prove public DOI-only recovery from fresh bootstrap" in text
    assert "Verify unauthenticated public metadata and file inventory" in text
    assert "repository_preservation_refresh.py seal" in text
    assert "archive: record refreshed repository preservation DOI" in text
    assert "PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK" in text
    assert "ZENODO_ACCESS_TOKEN" in text


def test_existing_preservation_controller_runs_inline_refresh_on_main_push():
    text = CONTROLLER.read_text(encoding="utf-8")
    assert "push:" in text
    assert "refresh-published-recovery:" in text
    assert "if: github.event_name == 'push'" in text
    assert "group: main-write-lock" in text
    assert "queue: max" in text
    assert "contents: write" in text
    assert "bash scripts/run_repository_preservation_refresh_ci.sh" in text
    assert "if: github.event_name != 'push'" in text
    assert "cancel-in-progress: false" in text
    assert "uses: ./.github/workflows/repository-preservation-refresh.yml" not in text


def test_repository_integrity_runs_refresh_only_after_full_main_gate():
    text = INTEGRITY.read_text(encoding="utf-8")
    assert "cancel-in-progress: false" in text
    assert "refresh-repository-preservation-doi:" in text
    assert "needs: current-system-integrity" in text
    assert "github.event_name == 'push'" in text
    assert "github.ref == 'refs/heads/main'" in text
    assert "group: main-write-lock" in text
    assert "queue: max" in text
    assert "contents: write" in text
    writer = text.split("  refresh-repository-preservation-doi:\n", 1)[1]
    assert "python3 -m pip install -r requirements-ci.txt" in writer
    assert writer.index("python3 -m pip install -r requirements-ci.txt") < writer.index(
        "bash scripts/run_repository_preservation_refresh_ci.sh"
    )
    assert "bash scripts/run_repository_preservation_refresh_ci.sh" in text
    assert "repository-preservation-refresh-proof-integrity" in text


def test_transaction_runner_is_strict_idempotent_and_publicly_verified():
    subprocess.run(["bash", "-n", str(RUNNER)], cwd=ROOT, check=True)
    text = RUNNER.read_text(encoding="utf-8")
    assert "set -euo pipefail" in text
    assert 'if [[ "$status" == "consumed" ]]' in text
    assert "archive: prepare repository preservation refresh v2" in text
    assert "--commit \"$source_sha\"" in text
    assert "--state preservation/repository-preservation-state-v2.json" in text
    assert "--zenodo-record-id \"$record_id\"" in text
    assert "repository_preservation_refresh.py verify-public" in text
    assert "repository_preservation_refresh.py seal" in text
    assert "archive: record refreshed repository preservation DOI" in text
    assert "git rebase origin/main" in text


def test_current_state_never_claims_live_main_equivalence():
    state = load(STATE)
    assert state["core_concept_doi"] == "10.5281/zenodo.21739343"
    assert state["external_binary_annexes"] == {
        "evidence": "10.5281/zenodo.21753937",
        "nft": "10.5281/zenodo.21754229",
    }
    assert state["self_describing_recovery_catalog"] == (
        "preservation/recovery-catalog.json"
    )
    assert state["live_main_equivalence_claimed"] is False


def test_consumed_refresh_has_complete_public_recovery_evidence():
    auth = load(AUTH)
    if auth["status"] != "consumed":
        assert auth["status"] in {"pending", "prepared"}
        return

    state = load(STATE)
    assert state["publication_status"] == "published_and_publicly_restored"
    assert state["public_download_verification"] == "passed"
    assert state["public_metadata_verification"] == "passed"
    assert state["public_cold_restore"] == "passed"

    versions = {entry["doi"]: entry for entry in state["versions"]}
    assert versions[auth["published_doi"]]["git_commit_sha"] == auth[
        "published_source_baseline_commit_sha"
    ]
    assert versions[auth["published_doi"]]["package_identity_sha256"] == auth[
        "published_package_identity_sha256"
    ]

    observation = load(OBSERVATION)
    assert observation["doi"] == auth["published_doi"]
    assert observation["source_baseline_commit_sha"] == auth[
        "published_source_baseline_commit_sha"
    ]
    assert observation["observed_without_github_credentials"] is True
    assert observation["observed_without_zenodo_credentials"] is True

    seq1 = load(ROOT / "preservation/current-baseline-publication-authorization-v1.json")
    assert seq1["status"] == "consumed"
    assert seq1["previous_core_version_doi"] == auth["published_doi"]
    assert versions[seq1["published_doi"]]["git_commit_sha"] == seq1[
        "published_source_baseline_commit_sha"
    ]
    assert versions[seq1["published_doi"]]["package_identity_sha256"] == seq1[
        "published_package_identity_sha256"
    ]

    seq2 = load(ROOT / "preservation/current-baseline-publication-authorization-v2.json")
    seq3 = load(ROOT / "preservation/current-baseline-publication-authorization-v3.json")
    assert seq2["status"] == "consumed"
    assert seq2["previous_core_version_doi"] == seq1["published_doi"]
    assert seq3["previous_core_version_doi"] == seq2["published_doi"]
    active = seq3 if seq3["status"] == "consumed" else seq2
    assert state["latest_doi"] == active["published_doi"]
    assert state["latest_git_commit_sha"] == active["published_source_baseline_commit_sha"]
    assert state["latest_package_identity_sha256"] == active["published_package_identity_sha256"]
    assert versions[seq2["published_doi"]]["git_commit_sha"] == seq2[
        "published_source_baseline_commit_sha"
    ]
    assert versions[seq2["published_doi"]]["package_identity_sha256"] == seq2[
        "published_package_identity_sha256"
    ]
    if seq3["status"] == "consumed":
        assert versions[seq3["published_doi"]]["git_commit_sha"] == seq3[
            "published_source_baseline_commit_sha"
        ]
        assert versions[seq3["published_doi"]]["package_identity_sha256"] == seq3[
            "published_package_identity_sha256"
        ]

    seq2_observation = load(
        ROOT / "preservation/current-baseline-publication-observation-v2.json"
    )
    assert seq2_observation["status"] == "passed"
    assert seq2_observation["version_doi"] == seq2["published_doi"]
    assert seq2_observation["source_git_commit_sha"] == seq2["published_source_baseline_commit_sha"]
    assert seq2_observation["public_cold_restore"] == "passed"
