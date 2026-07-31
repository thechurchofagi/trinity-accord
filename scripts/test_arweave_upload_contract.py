#!/usr/bin/env python3
"""Contract for crash-safe, weekly Arweave continuity publication."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    target = ROOT / path
    require(target.exists(), f"missing {path}")
    return target.read_text(encoding="utf-8")


def markers(text: str, required: list[str], label: str) -> None:
    for marker in required:
        require(marker in text, f"{label} missing: {marker}")


def main() -> int:
    uploader = read("scripts/arweave_upload_payload.mjs")
    markers(
        uploader,
        [
            "readback_sha256",
            "hash_match",
            "ARWEAVE_READBACK",
            "getData",
            "posted_pending_readback",
            "readback_failed",
            "retryable",
            "ARWEAVE_POST_CHECKPOINT",
            "ARWEAVE_RESUME_READBACK",
            "ARWEAVE_READBACK_MAX_SECONDS",
            "Refusing to resume transaction",
            "payload_sha256",
            "wallet_address_sha256",
            "arweave_archive_is_mirror_only",
            "bitcoin_originals_prevail",
        ],
        "generic uploader",
    )

    recorder = read("scripts/record_arweave_upload_result.py")
    markers(
        recorder,
        [
            'pick(data, "tx_id", "txid", "arweave_tx_id")',
            '"uploaded"',
            '"readback_failed"',
            '"posted_pending_readback"',
            "update_arweave_wallet_ledger.py",
            '"append-upload"',
        ],
        "wallet-ledger recorder",
    )

    builder = read("scripts/build_record_chain_arweave_archive.py")
    markers(
        builder,
        [
            'uploader = ROOT / "scripts" / "arweave_upload_payload.mjs"',
            'result_path = archive_dir / "upload-result.json"',
            'return read_json(result_path)',
            'upload_result.get("hash_match") is True',
            'upload_result.get("result") == "uploaded"',
            '"scripts/record_arweave_upload_result.py"',
            "load_native_chain_sources",
            'CHAIN_ID = "trinity-accord-public-reception-ledger"',
        ],
        "native archive builder",
    )

    runner = read("scripts/run_record_chain_arweave_archive.py")
    markers(
        runner,
        [
            "subprocess.TimeoutExpired",
            "builder.upload_to_arweave = guarded_upload",
            'partial["result"] = "readback_failed"',
            '"retry_readback"',
            "_find_incomplete_current_archive",
            "Resuming Arweave readback without a new paid post",
            "payload sha256 does not match",
        ],
        "crash-safe runner",
    )

    incremental = read("scripts/record_chain_arweave_incremental.py")
    markers(
        incremental,
        [
            "full_snapshot",
            "incremental_delta",
            "previous_archive_txid",
            "delta_record_count",
            "content_base64",
            "does not match the current chain prefix",
            "trinityaccord.weekly-continuity-bundle.v1",
            "trinityaccord.weekly-heartbeat-summary.v1",
            "trinityaccord.weekly-native-ots-evidence.v1",
            "proof_files_embedded_in_this_payload",
        ],
        "weekly incremental builder",
    )

    incremental_runner = read("scripts/run_record_chain_arweave_incremental.py")
    markers(
        incremental_runner,
        [
            "import run_record_chain_arweave_archive as runner",
            "build_incremental_payload_json",
            "runner.builder.build_payload_json = build_incremental_payload_json",
            "runner.main()",
            "evaluate_daily_spend",
            "readback-only resume",
        ],
        "incremental wrapper",
    )

    workflow = read(".github/workflows/record-chain-arweave-archive.yml")
    markers(
        workflow,
        [
            "run_record_chain_arweave_workflow_once.py",
            "secrets.ARKEY",
            "group: main-write-lock",
            "ARWEAVE_UPLOAD_TIMEOUT_SECONDS",
            "ARWEAVE_READBACK_MAX_SECONDS",
            "arweave_runtime_spend_guard.mjs",
            'cron: "17 7 * * 3"',
            "Automated upstream event is dry-run only",
            "detect_record_chain_pipeline_backlog.py",
            "ots_archivable_for_arweave",
            "weekly continuity archive",
        ],
        "weekly native archive workflow",
    )
    require('cron: "17 7 * * *"' not in workflow, "daily paid archive schedule must be retired")
    require(
        "run_record_chain_arweave_archive.py --mode" not in workflow,
        "workflow must not bypass the incremental wrapper",
    )

    orchestrator = read("scripts/run_record_chain_arweave_workflow_once.py")
    markers(
        orchestrator,
        [
            "verify_record_chain_arweave_archive.py",
            "trinity_record_chain.py",
            "--allow-stale-live-chain-tip",
            "checkpoint incomplete Arweave upload for safe readback resume",
            "Fail after persisting incomplete upload checkpoint",
            "push_without_reupload",
            "The Arweave uploader will not run again",
            "assert_clean_tracked_worktree",
        ],
        "bounded archive orchestrator",
    )
    retry = orchestrator.split("def push_without_reupload", 1)[-1].split("def main", 1)[0]
    require(
        "run_record_chain_arweave_incremental.py" not in retry,
        "metadata push retry must never repeat the paid upload",
    )

    runtime_guard = read("scripts/arweave_runtime_spend_guard.mjs")
    markers(
        runtime_guard,
        [
            "Daily paid Arweave upload limit reached",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "balance - reward < reserve",
            "!allowCanaryTags",
            "Canary-Record",
        ],
        "runtime spend guard",
    )

    retired_heartbeat = read(".github/workflows/waiting-heartbeat-capsule.yml")
    require("schedule:" not in retired_heartbeat, "standalone heartbeat upload must not be scheduled")
    require("ARKEY" not in retired_heartbeat, "retired heartbeat workflow must have no wallet capability")

    daily_native_ots = read(".github/workflows/native-ots-upgrade-watch.yml")
    for forbidden in ["ARKEY", "ARWEAVE_JWK", "--enable-paid-upload", "arweave_runtime_spend_guard.mjs"]:
        require(forbidden not in daily_native_ots, f"daily Native OTS must be no-cost: {forbidden}")

    retired_registry = read("scripts/update_record_chain_data_arweave_registry.py")
    require(
        "legacy record-chain data Arweave uploads are retired" in retired_registry,
        "legacy data registry updater must reject live writes",
    )
    require("would_write_registry" in retired_registry, "legacy updater must disclose read-only preview")
    require("write_json" not in retired_registry, "legacy updater must have no write helper")

    historical_verifier = read("scripts/verify_record_chain_data_arweave_registry.py")
    markers(
        historical_verifier,
        [
            "arweave_hash_match",
            "arweave_payload_sha256",
            "arweave_readback_sha256",
            "bundle_raw_file_sha256",
            "verify_bundle",
        ],
        "historical evidence verifier",
    )

    print("All weekly Arweave continuity upload/readback contract tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
