#!/usr/bin/env python3
"""Contract test for the weekly incremental Arweave continuity pipeline."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TERMS = {"ARV5", "LV5", "IVV5", "IPFS"}


def fail(errors: list[str]) -> None:
    print("Arweave archive contract tests FAILED:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    errors: list[str] = []
    workflow_path = ROOT / ".github/workflows/record-chain-arweave-archive.yml"
    required_scripts = [
        "scripts/build_record_chain_arweave_archive.py",
        "scripts/verify_record_chain_arweave_archive.py",
        "scripts/run_record_chain_arweave_archive.py",
        "scripts/record_chain_arweave_incremental.py",
        "scripts/run_record_chain_arweave_incremental.py",
        "scripts/run_record_chain_arweave_workflow_once.py",
        "scripts/detect_record_chain_pipeline_backlog.py",
    ]
    if not workflow_path.exists():
        errors.append("missing Record-Chain Arweave workflow")
        fail(errors)

    workflow = workflow_path.read_text(encoding="utf-8")
    required_workflow_markers = [
        "dry-run",
        "ARKEY",
        "detect_record_chain_pipeline_backlog.py",
        "arweave_archive_needed",
        "ots_matches_chain",
        "workflow_run",
        "Record Chain Head OTS Anchor",
        "Automated upstream event is dry-run only",
        'cron: "17 7 * * 3"',
        'if [ "$EVENT_NAME" = "schedule" ]; then',
        'mode="live"',
        'if [ "$EVENT_ACTOR" = "github-actions[bot]" ]; then',
        "run_record_chain_arweave_workflow_once.py",
        "weekly continuity archive",
        "ARWEAVE_MINIMUM_REMAINING_AR",
    ]
    for marker in required_workflow_markers:
        if marker not in workflow:
            errors.append(f"workflow missing weekly archive marker: {marker}")

    for forbidden in [
        'cron: "17 7 * * *"',
        "*/30 * * * *",
        "run_record_chain_arweave_archive.py --mode",
        "generate_public_home_status.py",
        "patch_public_home_status_primary.py",
        "api/public-home-status.json",
        "api/record-chain-status.json",
        "index.md",
        "sitemap.xml",
        "ARWEAVE_WALLET_JWK_B64",
        "echo $ARKEY",
        'echo "$ARKEY"',
        "set -x",
    ]:
        if forbidden in workflow:
            errors.append(f"workflow retains forbidden marker: {forbidden}")

    for relative in required_scripts:
        if not (ROOT / relative).exists():
            errors.append(f"missing {relative}")

    incremental_runner = (ROOT / "scripts/run_record_chain_arweave_incremental.py").read_text(encoding="utf-8")
    for marker in [
        "import run_record_chain_arweave_archive as runner",
        "build_incremental_payload_json",
        "runner.builder.build_payload_json = build_incremental_payload_json",
        "runner.main()",
        "evaluate_daily_spend",
    ]:
        if marker not in incremental_runner:
            errors.append(f"incremental runner missing marker: {marker}")

    orchestrator = (ROOT / "scripts/run_record_chain_arweave_workflow_once.py").read_text(encoding="utf-8")
    for marker in [
        "git fetch",
        "git rebase",
        "push_without_reupload",
        "The Arweave uploader will not run again",
        "run_record_chain_arweave_incremental.py",
    ]:
        if marker not in orchestrator:
            errors.append(f"bounded orchestrator missing marker: {marker}")
    retry = orchestrator.split("def push_without_reupload", 1)[-1].split("def main", 1)[0]
    if "run_record_chain_arweave_incremental.py" in retry:
        errors.append("metadata push retry must never invoke the paid uploader")
    if retry.find('"git", "rebase", "origin/main"') > retry.find('"git", "push", "origin", "HEAD:main"'):
        errors.append("metadata retry must rebase before push")

    builder = (ROOT / "scripts/record_chain_arweave_incremental.py").read_text(encoding="utf-8")
    for marker in [
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
        "daily_heartbeat_capsules_are_not_required",
    ]:
        if marker not in builder:
            errors.append(f"weekly continuity builder missing marker: {marker}")

    index_path = ROOT / "api/record-chain-arweave-index.json"
    if not index_path.exists():
        errors.append("missing api/record-chain-arweave-index.json")
    else:
        index = json.loads(index_path.read_text(encoding="utf-8"))
        if index.get("schema") != "trinityaccord.record-chain-arweave-index.v1":
            errors.append("Arweave index schema mismatch")
        boundary = index.get("boundary", {})
        for key in [
            "arweave_archive_is_mirror_only",
            "arweave_archive_is_not_authority",
            "arweave_archive_is_not_amendment",
            "bitcoin_originals_prevail",
        ]:
            if boundary.get(key) is not True:
                errors.append(f"Arweave index boundary missing: {key}")
        index_text = index_path.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if term in index_text:
                errors.append(f"forbidden term in Arweave index: {term}")

    home_sync = ROOT / ".github/workflows/homepage-status-sync.yml"
    if not home_sync.exists():
        errors.append("missing homepage status sync workflow")
    else:
        home_text = home_sync.read_text(encoding="utf-8")
        if "Record Chain Arweave Archive" not in home_text:
            errors.append("homepage status sync must listen to current archive workflow")
        if "scripts/update_public_generated_artifacts.py" not in home_text:
            errors.append("homepage status sync must use centralized generated-artifact updater")

    if errors:
        fail(errors)
    print("Arweave archive contract tests PASSED: weekly incremental continuity publication is bounded.")


if __name__ == "__main__":
    main()
