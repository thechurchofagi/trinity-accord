#!/usr/bin/env python3
"""Contract: automatic append/OTS with bounded weekly continuity publication.

External intake, append, and local Native OTS remain automatic. Upstream events
may request only free dry-run archive scans. One weekly schedule, or an explicit
human dispatch, may perform the paid incremental continuity upload containing
new records, heartbeat summary, and current mature OTS evidence.
"""
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


def main() -> None:
    append_workflow = read(".github/workflows/record-chain-append.yml")
    ots_workflow = read(".github/workflows/record-chain-head-ots-anchor.yml")
    arweave_workflow = read(".github/workflows/record-chain-arweave-archive.yml")
    heartbeat_workflow = read(".github/workflows/waiting-heartbeat-capsule.yml")
    native_ots_watch = read(".github/workflows/native-ots-upgrade-watch.yml")
    continuity_builder = read("scripts/record_chain_arweave_incremental.py")
    guard_script = read("scripts/check_record_chain_write_path_guard.py")
    detector_script = read("scripts/detect_record_chain_pipeline_backlog.py")
    home_sync_workflow = read(".github/workflows/homepage-status-sync.yml")

    require("name: Append Record Chain Entries" in append_workflow, "append workflow name mismatch")
    require(
        "Append record-chain entries from Render intake" in append_workflow,
        "append workflow must retain its approved commit message",
    )
    require("actions: write" in append_workflow, "append workflow must dispatch Native OTS")
    require(
        'gh workflow run record-chain-head-ots-anchor.yml --repo "$GITHUB_REPOSITORY" --ref main' in append_workflow,
        "append workflow must dispatch the Native OTS anchor workflow",
    )
    require("append_commit" in append_workflow, "append workflow must track its committed change")

    require("name: Homepage Status Sync" in home_sync_workflow, "homepage status sync is missing")
    for workflow_name in [
        "Record Chain Auto Finalize",
        "Append Record Chain Entries",
        "Record Chain Head OTS Anchor",
        "Record Chain Arweave Archive",
    ]:
        require(workflow_name in home_sync_workflow, f"homepage sync must listen to {workflow_name}")
    require(
        "scripts/update_public_generated_artifacts.py" in home_sync_workflow,
        "homepage sync must own centralized generated artifacts",
    )
    require(
        'gh workflow run deploy-pages.yml --repo "$GITHUB_REPOSITORY" --ref main' in home_sync_workflow,
        "homepage sync must explicitly dispatch Pages deployment",
    )

    for forbidden in [
        "generate_public_home_status.py",
        "patch_public_home_status_primary.py",
        "api/public-home-status.json",
        "index.md",
        "sitemap.xml",
    ]:
        require(forbidden not in append_workflow, f"append workflow must not write {forbidden}")
        require(forbidden not in ots_workflow, f"OTS anchor workflow must not write {forbidden}")
        require(forbidden not in arweave_workflow, f"Arweave workflow must not write {forbidden}")

    require('"Append Record Chain Entries"' in ots_workflow, "OTS workflow must listen to append")
    require('"Record Chain Auto Finalize"' in ots_workflow, "OTS workflow must listen to finalizer")
    require(
        "schedule:" in ots_workflow and "*/15 * * * *" in ots_workflow,
        "Native OTS anchor scan must remain every 15 minutes",
    )
    require("actions: write" in ots_workflow, "OTS anchor workflow must dispatch archive dry-runs")
    require("detect_record_chain_pipeline_backlog.py" in ots_workflow, "OTS anchor must use backlog detector")
    require("ots_anchor_needed" in ots_workflow, "OTS anchor must check ots_anchor_needed")
    require(
        'gh workflow run record-chain-arweave-archive.yml --repo "${GITHUB_REPOSITORY}" --ref main' in ots_workflow,
        "OTS anchor must dispatch the archive scanner",
    )
    require("-f upload_mode=dry-run" in ots_workflow, "OTS automation must dispatch dry-run only")
    require("-f upload_mode=live" not in ots_workflow, "OTS automation must never authorize paid mode")
    require(
        "git fetch origin main --prune" in ots_workflow and "git rebase origin/main" in ots_workflow,
        "OTS anchor push retry must fetch and rebase main",
    )

    require("workflow_run" in arweave_workflow, "archive workflow must support upstream dry-run events")
    require("Record Chain Head OTS Anchor" in arweave_workflow, "archive must listen to Native OTS")
    require(
        "Automated upstream event is dry-run only" in arweave_workflow,
        "upstream archive events must be dry-run only",
    )
    require(
        'cron: "17 7 * * 3"' in arweave_workflow,
        "Arweave workflow must have one weekly automated live schedule",
    )
    require('cron: "17 7 * * *"' not in arweave_workflow, "daily paid schedule must be retired")
    require("*/30 * * * *" not in arweave_workflow, "30-minute paid scanner must remain retired")
    require(
        'if [ "$EVENT_NAME" = "schedule" ]; then' in arweave_workflow and 'mode="live"' in arweave_workflow,
        "weekly schedule must explicitly resolve to live mode",
    )
    require(
        'if [ "$EVENT_ACTOR" = "github-actions[bot]" ]; then' in arweave_workflow,
        "bot dispatch must not authorize paid mode",
    )
    require(
        "run_record_chain_arweave_workflow_once.py" in arweave_workflow,
        "paid archive must use the bounded single-spend orchestrator",
    )
    require("detect_record_chain_pipeline_backlog.py" in arweave_workflow, "archive must use backlog detector")
    for marker in ["arweave_archive_needed", "ots_matches_chain", "ots_archivable_for_arweave", "ARKEY"]:
        require(marker in arweave_workflow, f"archive workflow missing: {marker}")

    for marker in [
        "trinityaccord.weekly-continuity-bundle.v1",
        "trinityaccord.weekly-heartbeat-summary.v1",
        "trinityaccord.weekly-native-ots-evidence.v1",
        "daily_heartbeat_capsules_are_not_required",
        "proof_files_embedded_in_this_payload",
    ]:
        require(marker in continuity_builder, f"weekly continuity payload missing: {marker}")

    require("schedule:" not in heartbeat_workflow, "standalone heartbeat capsule must have no schedule")
    require("workflow_run:" not in heartbeat_workflow, "standalone heartbeat capsule must not auto-trigger")
    require("ARKEY" not in heartbeat_workflow, "retired heartbeat workflow must have no wallet secret")
    require("contents: read" in heartbeat_workflow, "retired heartbeat workflow must be read-only")

    require('cron: "42 6 * * *"' in native_ots_watch, "daily no-cost OTS upgrade must remain scheduled")
    for forbidden in ["ARKEY", "ARWEAVE_JWK", "--enable-paid-upload", "arweave_runtime_spend_guard.mjs"]:
        require(forbidden not in native_ots_watch, f"daily Native OTS must not retain paid capability: {forbidden}")

    require("APPROVED_APPEND_MESSAGE" in guard_script, "write-path guard must define append message")
    require(
        "Append record-chain entries from Render intake" in guard_script,
        "write-path guard must allow approved append commit",
    )
    require("append workflow" in guard_script, "write-path guard must retain append approval path")
    require("api/record-chain-status.json" in guard_script, "write-path guard must classify status output")
    require(
        "trinity-record-chain-bot" in append_workflow or "github-actions[bot]" in append_workflow,
        "append workflow must use a bot identity",
    )
    require("git push" in append_workflow, "append workflow must push its durable result")

    for marker in ["ots_anchor_needed", "arweave_archive_needed", "pipeline_current", "--github-output"]:
        require(marker in detector_script, f"pipeline backlog detector missing: {marker}")

    print("PASS: automatic append/local OTS and bounded weekly continuity publication contract")


if __name__ == "__main__":
    main()
