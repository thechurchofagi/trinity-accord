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
    package_contract = read("scripts/weekly_continuity_package.py")
    assert "ZENODO_ACCESS_TOKEN" in workflow
    assert "GitHub Release" in workflow
    assert "gh release" not in workflow
    assert "/releases" not in workflow
    assert '"Authorization": f"Bearer {self.token}"' in publisher
    assert "access_token=" not in publisher
    assert "actions/newversion" in publisher
    assert "actions/publish" in publisher
    assert "PUBLISHED_FILE_NAMES" in publisher
    assert '"zenodo-metadata.json"' in package_contract
    assert "verify_remote_files" in publisher
    assert "TRINITY_WEEKLY_CONTINUITY_RIGHTS_V1_APPROVED" in publisher
    assert "WEEKLY_CONTINUITY_ZENODO_RIGHTS_ACK" in workflow
    assert "publication_enabled" in workflow
    assert "restore_weekly_continuity_archive.py" in workflow
    assert "trinityaccord.weekly-continuity-deposit.v1" in builder
    assert '"upload_type": "dataset"' in builder


def test_quarterly_remote_recovery_drill_covers_both_independent_mirrors():
    workflow = read(".github/workflows/quarterly-continuity-recovery.yml")
    assert 'cron: "17 8 1 1,4,7,10 *"' in workflow
    assert "--zenodo-record-id" in workflow
    assert "--arweave-txid" in workflow
    assert "restore_weekly_continuity_archive.py" in workflow
    assert "contents: read" in workflow
    assert "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02" in workflow


def test_feature_branch_has_no_temporary_patch_or_ci_write_boundary():
    assert not (ROOT / ".github/workflows/apply-heartbeat-retirement-contract-once.yml").exists()
    assert not (ROOT / "scripts/patch_waiting_heartbeat_retirement_contract_once.py").exists()
    current_tests = read(".github/workflows/run-current-tests.yml")
    assert "permissions:\n  contents: read" in current_tests
    assert "Apply and self-remove PR 825" not in current_tests
