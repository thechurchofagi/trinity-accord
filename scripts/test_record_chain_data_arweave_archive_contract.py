#!/usr/bin/env python3
"""Contract for retired legacy archives and the weekly native continuity route."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def require_markers(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        require(marker in text, f"{label} missing contract marker: {marker}")


def forbid_markers(text: str, markers: list[str], label: str) -> None:
    for marker in markers:
        require(marker not in text, f"{label} retains forbidden capability: {marker}")


def main() -> int:
    required = [
        "scripts/build_record_chain_data_arweave_bundle.py",
        "scripts/update_record_chain_data_arweave_registry.py",
        "scripts/verify_record_chain_data_arweave_bundle.py",
        "scripts/verify_record_chain_data_arweave_registry.py",
        "scripts/restore_record_chain_from_data_arweave_bundle.py",
        "scripts/test_legacy_arweave_retirement_behavior.py",
        "scripts/build_record_chain_arweave_archive.py",
        "scripts/run_record_chain_arweave_archive.py",
        "scripts/record_chain_arweave_incremental.py",
        "scripts/run_record_chain_arweave_incremental.py",
        "scripts/run_record_chain_arweave_workflow_once.py",
        ".github/workflows/record-chain-data-arweave-archive.yml",
        ".github/workflows/record-chain-arweave-archive.yml",
    ]
    for relative in required:
        require((ROOT / relative).exists(), f"missing {relative}")

    legacy_builder = (ROOT / "scripts/build_record_chain_data_arweave_bundle.py").read_text(encoding="utf-8")
    require_markers(
        legacy_builder,
        [
            "historical recovery/audit tooling only",
            "not_current_native_record_chain",
            "record_chain_data_delta",
            "record_chain_data_snapshot",
            "bundle_identity_sha256",
            "refusing to overwrite",
        ],
        "legacy builder",
    )
    require("utc_now" not in legacy_builder, "frozen legacy bundle identity must not depend on wall-clock time")

    legacy_updater = (ROOT / "scripts/update_record_chain_data_arweave_registry.py").read_text(encoding="utf-8")
    require_markers(
        legacy_updater,
        ["legacy record-chain data Arweave uploads are retired", "retired_read_only_preview"],
        "legacy updater",
    )
    require("write_json" not in legacy_updater, "retired registry updater must have no write helper")

    legacy_workflow = (ROOT / ".github/workflows/record-chain-data-arweave-archive.yml").read_text(encoding="utf-8")
    require_markers(
        legacy_workflow,
        [
            "Legacy Hash-Chain Data Archive Audit (Retired)",
            "permissions:\n  contents: read",
            "Confirm legacy-only source boundary",
            "Verify frozen legacy hash-chain view",
            "Prove audit did not mutate repository state",
        ],
        "retired workflow",
    )
    forbid_markers(
        legacy_workflow,
        [
            "contents: write",
            "secrets.ARKEY",
            "upload_mode:",
            "arweave_upload_payload.mjs",
            "git commit",
            "git push",
        ],
        "retired workflow",
    )

    workflow = (ROOT / ".github/workflows/record-chain-arweave-archive.yml").read_text(encoding="utf-8")
    require_markers(
        workflow,
        [
            "Record Chain Arweave Archive",
            "contents: write",
            "group: main-write-lock",
            "queue: max",
            "secrets.ARKEY",
            "run_record_chain_arweave_workflow_once.py",
            'cron: "17 7 * * 3"',
            "Automated upstream event is dry-run only",
            "weekly continuity archive",
            "ARWEAVE_MINIMUM_REMAINING_AR",
        ],
        "current weekly native archive workflow",
    )
    require(
        "run_record_chain_arweave_archive.py --mode" not in workflow,
        "workflow must not bypass the incremental payload route",
    )

    orchestrator = (ROOT / "scripts/run_record_chain_arweave_workflow_once.py").read_text(encoding="utf-8")
    require_markers(
        orchestrator,
        [
            "run_record_chain_arweave_incremental.py",
            "push_without_reupload",
            "The Arweave uploader will not run again",
        ],
        "single-spend archive orchestrator",
    )
    retry = orchestrator.split("def push_without_reupload", 1)[-1].split("def main", 1)[0]
    require(
        "run_record_chain_arweave_incremental.py" not in retry,
        "metadata push retry must never repeat the paid uploader",
    )

    incremental = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text(encoding="utf-8")
    require_markers(
        incremental,
        [
            "incremental_delta",
            "full_snapshot",
            "previous_archive_txid",
            "previous_native_record_count",
            "delta_record_count",
            "content_base64",
            "does not match the current chain prefix",
            "trinityaccord.weekly-continuity-bundle.v1",
            "trinityaccord.weekly-heartbeat-summary.v1",
            "trinityaccord.weekly-native-ots-evidence.v1",
            "proof_files_embedded_in_this_payload",
            "daily_heartbeat_capsules_are_not_required",
        ],
        "weekly incremental continuity builder",
    )

    incremental_runner = (ROOT / "scripts/run_record_chain_arweave_incremental.py").read_text(encoding="utf-8")
    require_markers(
        incremental_runner,
        [
            "import run_record_chain_arweave_archive as runner",
            "build_incremental_payload_json",
            "runner.builder.build_payload_json = build_incremental_payload_json",
            "runner.main()",
        ],
        "incremental archive runner",
    )

    home_sync = (ROOT / ".github/workflows/homepage-status-sync.yml").read_text(encoding="utf-8")
    require(
        '      - "Record Chain Arweave Archive"' in home_sync,
        "homepage sync must listen to current native archive",
    )
    require(
        '      - "Record Chain Data Arweave Archive"' not in home_sync,
        "homepage sync must not listen to retired legacy archive",
    )

    behavior = subprocess.run(
        [sys.executable, "scripts/test_legacy_arweave_retirement_behavior.py"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(
        behavior.returncode == 0,
        "legacy archive behavioral contract failed:\n" + (behavior.stderr or behavior.stdout)[-4000:],
    )

    print(
        "PASS: legacy hash-chain archive is retired; weekly incremental native "
        "continuity archive is the only paid Record-Chain route"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
