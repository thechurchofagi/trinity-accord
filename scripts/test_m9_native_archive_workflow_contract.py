#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require_contains(path: Path, text: str, errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    if text not in body:
        errors.append(f"{path.relative_to(ROOT)} missing: {text}")


def require_not_contains(path: Path, text: str, errors: list[str]) -> None:
    body = path.read_text(encoding="utf-8")
    if text in body:
        errors.append(f"{path.relative_to(ROOT)} must not contain: {text}")


def main() -> None:
    errors: list[str] = []

    head_wf = ROOT / ".github" / "workflows" / "record-chain-head-ots-anchor.yml"
    tip_helper = ROOT / "scripts" / "check_native_ots_latest_matches_chain_tip.py"
    arweave_wf = ROOT / ".github" / "workflows" / "record-chain-arweave-archive.yml"
    arweave_runner = ROOT / "scripts" / "run_record_chain_arweave_archive.py"
    incremental_runner = ROOT / "scripts" / "run_record_chain_arweave_incremental.py"
    incremental_builder = ROOT / "scripts" / "record_chain_arweave_incremental.py"
    workflow_runner = ROOT / "scripts" / "run_record_chain_arweave_workflow_once.py"
    runtime_guard = ROOT / "scripts" / "arweave_runtime_spend_guard.mjs"
    data_wf = ROOT / ".github" / "workflows" / "record-chain-data-arweave-archive.yml"

    if not head_wf.exists():
        errors.append("missing .github/workflows/record-chain-head-ots-anchor.yml")
    else:
        for marker in [
            "Record Chain Head OTS Anchor",
            "requirements-ci.txt",
            "trinity_record_chain.py verify",
            "ots_anchor_native_record_chain_head.py",
            "record-chain/ots/native-anchors",
            "check_native_ots_latest_matches_chain_tip.py",
            '"Record Chain Auto Finalize"',
            '"Append Record Chain Entries"',
            "head_branch == 'main'",
            "git push origin HEAD:main",
        ]:
            require_contains(head_wf, marker, errors)

        for forbidden in [
            "ots_anchor_record_chain_head.py",
            "main.chain.jsonl",
            "api/record-chain-head.json",
            "record-chain-ots-latest.json",
            "record-chain/ots/anchors",
            "verify_record_chain_integrity.py",
            "${GITHUB_REF_NAME",
        ]:
            require_not_contains(head_wf, forbidden, errors)

        head_text = head_wf.read_text(encoding="utf-8")
        if head_text.count("check_native_ots_latest_matches_chain_tip.py") < 2:
            errors.append("record-chain-head-ots-anchor.yml must revalidate the native OTS tip after rebase")

    if not tip_helper.exists():
        errors.append("missing scripts/check_native_ots_latest_matches_chain_tip.py")
    else:
        for marker in [
            "record-chain/chain-tip.json",
            "api/record-chain-native-ots-latest.json",
            "legacy_main_chain_jsonl_is_not_source",
            "latest_record_id",
            "latest_record_sha256",
            "native_record_count",
            "latest_anchored_file",
            "latest_anchor_file",
            "latest_ots_file",
            "trinity-accord-public-reception-ledger",
        ]:
            require_contains(tip_helper, marker, errors)
        require_not_contains(tip_helper, "record-chain/hash-chain/main.chain.jsonl", errors)

    if not arweave_wf.exists():
        errors.append("missing .github/workflows/record-chain-arweave-archive.yml")
    else:
        for marker in [
            "Record Chain Arweave Archive",
            "Record Chain Head OTS Anchor",
            "run_record_chain_arweave_incremental.py",
            "run_record_chain_arweave_workflow_once.py",
            "detect_record_chain_pipeline_backlog.py",
            "arweave_archive_needed",
            "ots_matches_chain",
            "ots_archivable_for_arweave",
            "ARKEY",
            "arweave_runtime_spend_guard.mjs",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            'cron: "17 7 * * *"',
            "Automated upstream event is dry-run only",
            'if [ "$EVENT_ACTOR" = "github-actions[bot]" ]; then',
        ]:
            require_contains(arweave_wf, marker, errors)

        for forbidden in [
            'workflows: ["Record Chain Anchor"]',
            "build_record_chain_data_arweave_bundle.py",
            "record-chain-arweave-data-registry.json",
            "*/30 * * * *",
            "run_record_chain_arweave_archive.py --mode",
            "echo $ARKEY",
        ]:
            require_not_contains(arweave_wf, forbidden, errors)

    if not workflow_runner.exists():
        errors.append("missing scripts/run_record_chain_arweave_workflow_once.py")
    else:
        for marker in [
            "verify_record_chain_arweave_archive.py",
            "trinity_record_chain.py",
            "--allow-stale-live-chain-tip",
            "record-chain/arweave-archives/",
            "api/record-chain-arweave-index.json",
            "record-chain/arweave-backlog.json",
            "api/record-chain-arweave-backlog.json",
            "record-chain/ots/native-ots-backlog.json",
            "api/record-chain-native-ots-backlog.json",
            "record-chain/arweave-wallet-ledger.json",
            "checkpoint incomplete Arweave upload for safe readback resume",
            "Fail after persisting incomplete upload checkpoint",
            "assert_clean_tracked_worktree",
            "push_without_reupload",
            "The Arweave uploader will not run again",
        ]:
            require_contains(workflow_runner, marker, errors)

        runner_text = workflow_runner.read_text(encoding="utf-8")
        retry_block = runner_text.split("def push_without_reupload", 1)[-1].split("def main", 1)[0]
        if "run_record_chain_arweave_incremental.py" in retry_block:
            errors.append("bounded archive retry block must not invoke a paid upload")
        clean_index = retry_block.find("assert_clean_tracked_worktree()")
        fetch_index = retry_block.find('run("git", "fetch", "origin", "main", "--prune")')
        rebase_index = retry_block.find('run("git", "rebase", "origin/main"')
        push_index = retry_block.find('run("git", "push", "origin", "HEAD:main"')
        if min(clean_index, fetch_index, rebase_index, push_index) < 0:
            errors.append("bounded archive retry block is missing clean/fetch/rebase/push sequencing")
        elif not (clean_index < fetch_index < rebase_index < push_index):
            errors.append("bounded archive retry block must check clean state, fetch, rebase, then push")

    if not arweave_runner.exists():
        errors.append("missing scripts/run_record_chain_arweave_archive.py")
    else:
        for marker in [
            "import build_record_chain_arweave_archive as builder",
            "builder.build_archive_manifest",
            "builder.upload_to_arweave = guarded_upload",
            "Resuming Arweave readback without a new paid post",
            "subprocess.TimeoutExpired",
        ]:
            require_contains(arweave_runner, marker, errors)

    if not incremental_runner.exists():
        errors.append("missing scripts/run_record_chain_arweave_incremental.py")
    else:
        for marker in [
            "import run_record_chain_arweave_archive as runner",
            "build_incremental_payload_json",
            "runner.builder.build_payload_json = build_incremental_payload_json",
            "runner.main()",
            "evaluate_daily_spend",
        ]:
            require_contains(incremental_runner, marker, errors)

    if not incremental_builder.exists():
        errors.append("missing scripts/record_chain_arweave_incremental.py")
    else:
        for marker in [
            "full_snapshot",
            "incremental_delta",
            "previous_archive_txid",
            "delta_record_count",
            "content_base64",
            "does not match the current chain prefix",
        ]:
            require_contains(incremental_builder, marker, errors)

    if not runtime_guard.exists():
        errors.append("missing scripts/arweave_runtime_spend_guard.mjs")
    else:
        for marker in [
            "Daily paid Arweave upload limit reached",
            "ARWEAVE_MINIMUM_REMAINING_AR",
            "balance - reward < reserve",
            "Canary-Record",
            "!allowCanaryTags",
        ]:
            require_contains(runtime_guard, marker, errors)

    if not data_wf.exists():
        errors.append("missing .github/workflows/record-chain-data-arweave-archive.yml")
    else:
        require_contains(data_wf, "build_record_chain_data_arweave_bundle.py", errors)
        require_not_contains(data_wf, "ots_anchor_native_record_chain_head.py", errors)
        require_not_contains(data_wf, "record-chain-native-ots-latest.json", errors)

    if errors:
        print("M9 native archive workflow contract FAILED:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        raise SystemExit(1)

    print("M9 crash-safe incremental native archive workflow contract PASSED.")


if __name__ == "__main__":
    main()
