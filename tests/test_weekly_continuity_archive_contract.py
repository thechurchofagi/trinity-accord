from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def test_standalone_heartbeat_paid_upload_is_retired():
    workflow = read(".github/workflows/waiting-heartbeat-capsule.yml")
    assert "schedule:" not in workflow
    assert "workflow_run:" not in workflow
    assert "ARKEY" not in workflow
    assert "arweave_upload_waiting_heartbeat_capsule" not in workflow
    assert "contents: read" in workflow


def test_record_chain_paid_archive_is_weekly_and_incremental():
    workflow = read(".github/workflows/record-chain-arweave-archive.yml")
    assert 'cron: "17 7 * * 3"' in workflow
    assert 'cron: "17 7 * * *"' not in workflow
    assert "run_record_chain_arweave_workflow_once.py" in workflow
    assert "weekly continuity archive" in workflow.lower()
    assert "Automated upstream event is dry-run only" in workflow


def test_daily_native_ots_has_no_paid_arweave_path():
    workflow = read(".github/workflows/native-ots-upgrade-watch.yml")
    runner = read("scripts/run_native_ots_workflow_once.py")
    assert "upgrade_only" in workflow
    assert "ARKEY" not in workflow
    assert "ARWEAVE_JWK" not in workflow
    assert "enable-paid-upload" not in workflow
    assert "enable-paid-upload" not in runner
    assert "evaluate_daily_spend" not in runner
    assert '{"verify_only", "upgrade_only"}' in runner


def test_weekly_payload_embeds_heartbeat_and_native_ots_evidence():
    script = read("scripts/record_chain_arweave_incremental.py")
    assert "trinityaccord.weekly-continuity-bundle.v1" in script
    assert "trinityaccord.weekly-heartbeat-summary.v1" in script
    assert "trinityaccord.weekly-native-ots-evidence.v1" in script
    assert '"latest_anchor_file"' in script
    assert '"latest_anchored_file"' in script
    assert '"latest_ots_file"' in script
    assert "content_base64" in script
    assert "daily_heartbeat_capsules_are_not_required" in script


def test_zenodo_publisher_is_independent_and_token_safe():
    workflow = read(".github/workflows/weekly-continuity-zenodo.yml")
    publisher = read("scripts/publish_weekly_continuity_to_zenodo.py")
    builder = read("scripts/build_weekly_continuity_deposit.py")
    assert "ZENODO_ACCESS_TOKEN" in workflow
    assert "GitHub Release" in workflow
    assert "gh release" not in workflow
    assert "/releases" not in workflow
    assert '"Authorization": f"Bearer {self.token}"' in publisher
    assert "access_token=" not in publisher
    assert "actions/newversion" in publisher
    assert "actions/publish" in publisher
    assert "trinityaccord.weekly-continuity-deposit.v1" in builder
    assert '"upload_type": "dataset"' in builder
