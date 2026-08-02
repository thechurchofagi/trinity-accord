from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/external-binary-annex-publication.yml"


def test_runner_context_is_not_used_in_job_level_environment():
    text = WORKFLOW.read_text(encoding="utf-8")
    job_env = text.split("    env:\n", 1)[1].split("\n\n    steps:", 1)[0]
    assert "runner.temp" not in job_env
    assert "EVIDENCE_PACKAGE_DIR" not in job_env
    assert "NFT_PACKAGE_DIR" not in job_env


def test_runner_local_paths_are_initialized_through_github_env():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "Initialize runner-local package paths" in text
    assert '"$RUNNER_TEMP/trinity-evidence-annex-v3" >> "$GITHUB_ENV"' in text
    assert '"$RUNNER_TEMP/trinity-nft-annex-v3" >> "$GITHUB_ENV"' in text
    assert '--output-dir "$EVIDENCE_PACKAGE_DIR"' in text
    assert '--output-dir "$NFT_PACKAGE_DIR"' in text


def test_queue_and_safe_main_write_contracts_remain_present():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert "group: main-write-lock" in text
    assert "queue: max" in text
    assert "cancel-in-progress: false" in text
    assert "git fetch origin main --prune" in text
    assert "git rebase origin/main" in text
