from __future__ import annotations

import json
import pathlib
import subprocess


ROOT = pathlib.Path(__file__).resolve().parents[1]
AUTH = ROOT / "preservation/current-baseline-publication-authorization-v2.json"
STATE_MACHINE = ROOT / "scripts/current_baseline_publication_v2.py"
RUNNER = ROOT / "scripts/run_current_baseline_publication_v2_ci.sh"
DISPATCHER = ROOT / "scripts/run_repository_preservation_refresh_ci.sh"
SEQ1_AUTH = ROOT / "preservation/current-baseline-publication-authorization-v1.json"


def test_sequence2_authorization_is_exact_and_current_state_is_valid():
    auth = json.loads(AUTH.read_text(encoding="utf-8"))
    assert auth["schema"] == "trinityaccord.current-baseline-publication-authorization.v2"
    assert auth["sequence"] == 2
    assert auth["status"] in {"pending", "prepared", "consumed"}
    assert auth["core_concept_doi"] == "10.5281/zenodo.21739343"
    assert auth["previous_core_version_doi"] == "10.5281/zenodo.21831412"
    assert auth["required_proof_hardening_commit_sha"] == "0cdba0d13b97f242908f150b634ae7a481be9ee3"
    assert auth["include_full_repository_doi"] is True
    assert auth["include_homepage_arweave_snapshot"] is False
    assert auth["non_amending_boundary"] is True
    assert auth["live_main_equivalence_claimed"] is False
    subprocess.run(["python3", str(STATE_MACHINE), "validate"], cwd=ROOT, check=True)


def test_sequence1_history_is_not_reopened_or_rewritten():
    seq1 = json.loads(SEQ1_AUTH.read_text(encoding="utf-8"))
    assert seq1["status"] == "consumed"
    assert seq1["published_doi"] == "10.5281/zenodo.21831412"
    assert seq1["homepage_snapshot_arweave_txid"] == "-lAi9yvTzgfDTx32n8nzNRKAGOegO_croyzNHX3y7IM"
    assert seq1["homepage_snapshot_sha256"] == "361f0a1479e48fc5b194f19a65929a1dad53c1264a593e163eb24b3cacc8be63"


def test_sequence2_runner_is_zenodo_only_and_idempotent_publisher_based():
    subprocess.run(["bash", "-n", str(RUNNER)], cwd=ROOT, check=True)
    text = RUNNER.read_text(encoding="utf-8")
    assert "publish_preservation_capsule_to_zenodo_v3.py" in text
    assert "restore-trinity-accord.py" in text
    assert "ARKEY" not in text
    assert "arweave_upload_homepage_snapshot" not in text
    assert "record_arweave_upload_result" not in text
    assert "required_proof_hardening_commit_sha" in text
    assert "git diff --quiet" in text


def test_integrity_dispatcher_prioritizes_sequence2_before_sequence1():
    subprocess.run(["bash", "-n", str(DISPATCHER)], cwd=ROOT, check=True)
    text = DISPATCHER.read_text(encoding="utf-8")
    v2 = text.index("current-baseline-publication-authorization-v2.json")
    v1 = text.index("current-baseline-publication-authorization-v1.json")
    assert v2 < v1
    assert "run_current_baseline_publication_v2_ci.sh" in text
