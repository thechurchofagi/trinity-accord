#!/usr/bin/env python3
"""Contract for the retired scheduled paid-repair path.

The former hourly live repair workflow is now a daily read-only visibility scan.
The underlying processor still exposes explicit operator-only live routing, but
scheduled automation must have no wallet secret, write permission, paid flag,
or Git push capability. Paid repair is handled by the primary bounded workflows
with daily ledger and transaction-time reserve gates.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(rel: str) -> str:
    path = ROOT / rel
    require(path.exists(), f"missing {rel}")
    return path.read_text(encoding="utf-8")


def main() -> int:
    workflow = read(".github/workflows/archive-backlog-repair.yml")
    processor = read("scripts/process_archive_backlog.py")
    builder = read("scripts/build_record_chain_arweave_archive.py")
    uploader = read("scripts/arweave_upload_payload.mjs")
    runner = read("scripts/run_native_ots_upgrade_verify.py")
    runtime_guard = read("scripts/arweave_runtime_spend_guard.mjs")
    daily_guard = read("scripts/arweave_daily_spend_guard.py")

    # Scheduled surface: daily, read-only and dry-run only.
    for needle in [
        "workflow_dispatch:",
        'cron: "47 8 * * *"',
        "contents: read",
        "group: archive-backlog-scan",
        "timeout-minutes: 15",
        "actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5",
        "ref: main",
        "python3 scripts/detect_archive_backlog.py --write",
        "--kind record_chain_arweave",
        "--kind native_ots_bundle",
        "--max-items 1",
        "--mode dry-run",
        "This scheduled workflow never uploads to Arweave",
        "Paid repair requires an explicit human dispatch",
    ]:
        require(needle in workflow, f"read-only backlog workflow missing {needle}")

    for forbidden in [
        'cron: "17 * * * *"',
        "contents: write",
        "group: main-write-lock",
        "--mode live",
        "--enable-paid-upload",
        "secrets.ARKEY",
        "vars.ARKEY",
        "ARWEAVE_JWK",
        "generate_arweave_wallet_status.py",
        "arweave-wallet-ledger.json",
        "arweave-wallet-status.json",
        "git add",
        "git commit",
        "git push",
        "git rebase",
        "record-chain/arweave-archives/",
        "api/record-chain-arweave-index.json",
    ]:
        require(forbidden not in workflow, f"scheduled backlog scan retains paid/write capability: {forbidden}")

    # Processor dry-run is structurally before every mutator. Explicit manual
    # live mode remains available for operators but is never scheduled here.
    for needle in [
        "dry_run_preview",
        'if args.mode == "dry-run"',
        '"repository_mutation": False',
        '"subprocess_execution": False',
        '"would_increment_retry_count": False',
        "waiting_for_key",
        "upgrade_due",
        "upgrade_failed",
        "upgrade_native_ots_anchor",
        "retry_native_ots_upgrade",
        "upload_failed",
        "readback_failed",
        "archived",
        "retry_count",
        "last_attempt_at",
        "last_error",
        "next_action",
    ]:
        require(needle in processor, f"processor missing {needle}")
    require(
        processor.find('if args.mode == "dry-run"')
        < processor.find("run_detector_write()", processor.find("def main")),
        "processor must route dry-run before detector writes",
    )
    require(
        "return process_native_ots(args.max_items, args.enable_paid_upload)" in processor,
        "explicit operator-only live Native OTS route missing",
    )

    # Low-level crash safety and state vocabulary remain intact.
    for needle in [
        "posted_pending_readback",
        "readback_failed",
        "retryable",
        "function writeResult",
        "fs.writeFileSync",
        "outPath",
        "ARWEAVE_POST_CHECKPOINT",
        "ARWEAVE_RESUME_READBACK",
    ]:
        require(needle in uploader, f"uploader missing durable result marker {needle}")
    for needle in [
        "archive_status",
        "waiting_for_key",
        "upload_failed",
        "readback_failed",
        "hash_match",
        "refresh_archive_backlog",
    ]:
        require(needle in builder, f"record-chain archive builder missing {needle}")
    for needle in [
        "--anchor-file",
        "--all-backlog",
        "--max-items",
        "upgrade_due",
        "upgrade_failed",
        "waiting_for_key",
        "upload_failed",
        "readback_failed",
        "arweave_archived",
        "is_current_latest_anchor",
    ]:
        require(needle in runner, f"native OTS runner missing {needle}")

    # Primary paid paths enforce daily count, reserve, and production metadata at
    # the transaction boundary; the read-only scan cannot bypass these guards.
    for needle in [
        "Daily paid Arweave upload limit reached",
        "ARWEAVE_MINIMUM_REMAINING_AR",
        "balance - reward < reserve",
        "!allowCanaryTags",
    ]:
        require(needle in runtime_guard, f"runtime spend guard missing {needle}")
    for needle in [
        '"record_chain_arweave_archive": 1',
        '"native_ots_bundle_archive": 1',
        "daily_paid_upload_limit_reached",
        "paid_at",
    ]:
        require(needle in daily_guard, f"daily spend guard missing {needle}")

    behavior = ROOT / "scripts/test_archive_backlog_dry_run_behavior.py"
    require(behavior.exists(), "archive backlog dry-run behavior test missing")
    result = subprocess.run(
        [sys.executable, str(behavior)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    require(
        result.returncode == 0,
        "archive backlog dry-run behavior failed:\n" + (result.stderr or result.stdout)[-5000:],
    )

    # This no-write workflow must not directly touch homepage state either.
    for forbidden in [
        "generate_record_chain_status.py",
        "generate_public_home_status.py",
        "patch_public_home_status_primary.py",
        "api/public-home-status.json",
        "api/record-chain-status.json",
        "index.md",
        "sitemap.xml",
    ]:
        require(
            forbidden not in workflow,
            f"archive backlog scan must not directly write homepage status: {forbidden}",
        )

    print("PASS: scheduled archive backlog path is a daily read-only scan; paid repair cannot bypass cost guards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
