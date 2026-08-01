from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess

import pytest

from scripts import arweave_daily_spend_guard as spend_guard
from scripts.arweave_daily_spend_guard import evaluate_daily_spend

ROOT = Path(__file__).resolve().parents[1]


def test_daily_spend_guard_blocks_second_same_kind(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "kind": "record_chain_arweave_archive",
                        "status": "paid",
                        "paid_at": "2026-07-31T01:02:03Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decision = evaluate_daily_spend(
        "record_chain_arweave_archive",
        ledger_path=ledger,
        now=datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc),
    )
    assert decision.allowed is False
    assert decision.reason == "daily_paid_upload_limit_reached"
    assert decision.paid_count == 1
    assert decision.daily_limit == 1


def test_daily_spend_guard_keeps_kinds_independent(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.json"
    ledger.write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "kind": "record_chain_arweave_archive",
                        "status": "paid",
                        "paid_at": "2026-07-31T01:02:03Z",
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    decision = evaluate_daily_spend(
        "native_ots_bundle_archive",
        ledger_path=ledger,
        now=datetime(2026, 7, 31, 12, 0, tzinfo=timezone.utc),
    )
    assert decision.allowed is True


def test_scheduled_backlog_job_has_no_paid_path() -> None:
    workflow = (ROOT / ".github/workflows/archive-backlog-repair.yml").read_text()
    assert 'cron: "17 * * * *"' not in workflow
    assert 'cron: "47 8 * * *"' in workflow
    assert "--mode live" not in workflow
    assert "enable-paid-upload" not in workflow
    assert "contents: read" in workflow


def test_record_chain_workflow_uses_single_spend_orchestrator_weekly() -> None:
    workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text()
    orchestrator = (ROOT / "scripts/run_record_chain_arweave_workflow_once.py").read_text()
    assert 'cron: "17 7 * * 3"' in workflow
    assert 'cron: "17 7 * * *"' not in workflow
    assert "run_record_chain_arweave_workflow_once.py" in workflow
    assert "arweave_runtime_spend_guard.mjs" in workflow
    assert "The Arweave uploader will not run again" in orchestrator
    assert orchestrator.count("run_record_chain_arweave_incremental.py") == 2
    retry = orchestrator.split("def push_without_reupload", 1)[1].split("def main", 1)[0]
    assert "run_record_chain_arweave_incremental.py" not in retry


def test_native_ots_daily_workflow_has_no_paid_path() -> None:
    workflow = (ROOT / ".github/workflows/native-ots-upgrade-watch.yml").read_text()
    orchestrator = (ROOT / "scripts/run_native_ots_workflow_once.py").read_text()
    weekly_builder = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text()
    assert "run_native_ots_workflow_once.py" in workflow
    assert "upgrade_only" in workflow
    for forbidden in [
        "ARKEY",
        "ARWEAVE_JWK",
        "arweave_runtime_spend_guard.mjs",
        "--enable-paid-upload",
    ]:
        assert forbidden not in workflow
    for forbidden in ["evaluate_daily_spend", "--enable-paid-upload", "ARWEAVE_JWK_PATH"]:
        assert forbidden not in orchestrator
    retry = orchestrator.split("def push_metadata_only", 1)[1].split("def main", 1)[0]
    assert "run_native_ots_upgrade_verify.py" not in retry
    assert "trinityaccord.weekly-native-ots-evidence.v1" in weekly_builder


def test_standalone_heartbeat_workflow_has_no_paid_path() -> None:
    workflow = (ROOT / ".github/workflows/waiting-heartbeat-capsule.yml").read_text()
    assert "schedule:" not in workflow
    assert "workflow_run:" not in workflow
    assert "ARKEY" not in workflow
    assert "arweave_upload_waiting_heartbeat_capsule" not in workflow
    assert "contents: read" in workflow


def test_runtime_guard_enforces_reserve_daily_limit_and_non_canary_metadata() -> None:
    source = (ROOT / "scripts/arweave_runtime_spend_guard.mjs").read_text()
    assert 'DEFAULT_RESERVE_AR = "0.25"' in source
    assert "Daily paid Arweave upload limit reached" in source
    assert "balance - reward < reserve" in source
    assert 'DEFAULT_MAX_TRANSACTION_REWARD_AR = "0.05"' in source
    assert 'DEFAULT_ROLLING_30_DAY_SPEND_AR = "0.50"' in source
    assert "DEFAULT_MAX_PAYLOAD_BYTES = 8 * 1024 * 1024" in source
    assert "rollingPaid + reward > rollingLimit" in source
    assert "payloadBytes > limit" in source
    assert "reward > maxReward" in source
    assert "if (" in source and "Canary-Record" in source
    assert "!allowCanaryTags" in source


def test_weekly_workflow_pins_paid_arweave_budget_limits() -> None:
    workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text()
    assert 'ARWEAVE_MAX_PAYLOAD_BYTES: "8388608"' in workflow
    assert 'ARWEAVE_MAX_TRANSACTION_REWARD_AR: "0.05"' in workflow
    assert 'ARWEAVE_ROLLING_30_DAY_SPEND_LIMIT_AR: "0.50"' in workflow


def test_runtime_budget_helpers_execute() -> None:
    result = subprocess.run(
        ["node", "scripts/test_arweave_runtime_spend_guard_budgets.mjs"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    assert "PASS:" in result.stdout


def test_daily_paid_limit_cannot_be_raised_above_one(monkeypatch) -> None:
    monkeypatch.setenv("ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT", "2")
    with pytest.raises(RuntimeError, match="unsafe daily Arweave limit"):
        spend_guard._daily_limit("record_chain_arweave_archive")


def test_cooldown_missing_history_fails_closed() -> None:
    source = (ROOT / "apps/record_chain_intake_gateway/secure_entrypoint.py").read_text()
    assert "TRINITY_ALLOW_EMPTY_INTAKE_HISTORY" in source
    assert "refusing to fail open" in source


def test_incremental_delta_checks_prefix_sha_and_embeds_continuity() -> None:
    source = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text()
    assert "does not match the current chain prefix" in source
    assert 'prefix_ref.get("record_sha256") != previous_latest_sha' in source
    assert "trinityaccord.weekly-continuity-bundle.v1" in source
    assert "trinityaccord.weekly-heartbeat-summary.v1" in source
    assert "trinityaccord.weekly-native-ots-evidence.v1" in source
