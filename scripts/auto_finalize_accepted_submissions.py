#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "record-chain/hash-chain/main.chain.jsonl"
AGENT_START = ROOT / "api/agent-start.v2.json"

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

def run(cmd: list[str]) -> None:
    result = subprocess.run(cmd, cwd=ROOT, text=True)
    if result.returncode != 0:
        raise SystemExit(f"command failed: {' '.join(cmd)}")

def existing_receipt_ids() -> set[str]:
    out: set[str] = set()
    for entry in read_jsonl(LEDGER):
        rid = entry.get("receipt_id")
        if isinstance(rid, str) and rid:
            out.add(rid)
    return out

def current_confirm_string() -> str:
    """Return the correct confirm string based on the active public test phase."""
    agent = read_json(AGENT_START)
    phase = (((agent.get("public_phase") or {}).get("network_phase")) or "prelaunch")
    if phase == "live_test":
        return "I_UNDERSTAND_THIS_APPENDS_A_MAINNET_LIVE_TEST_RECORD"
    return "I_UNDERSTAND_THIS_APPENDS_A_MAINNET_PRELAUNCH_TEST_RECORD"

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--submissions-dir", default="record-chain/intake/accepted/submissions")
    ap.add_argument("--receipts-dir", default="record-chain/intake/accepted/receipts")
    ap.add_argument("--max-records", type=int, default=10)
    ap.add_argument("--source-run-id", default="auto-finalize")
    ap.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    ap.add_argument("--require-new-records", action="store_true", default=False,
                    help="Exit non-zero if no new records were finalized (prevents no-op false success).")
    args = ap.parse_args()

    submissions_dir = ROOT / args.submissions_dir
    receipts_dir = ROOT / args.receipts_dir

    if not submissions_dir.exists() or not receipts_dir.exists():
        exit_code = 1 if args.require_new_records else 0
        print(json.dumps({
            "result": "fail" if args.require_new_records else "pass",
            "mode": args.mode,
            "finalized_count": 0,
            "skipped_count": 0,
            "reason": "intake directories missing; no-op"
        }, indent=2, sort_keys=True))
        return exit_code

    existing = existing_receipt_ids()
    finalized = []
    skipped = []

    confirm = current_confirm_string()

    for sub in sorted(submissions_dir.glob("*.submission.json")):
        if len(finalized) >= args.max_records:
            break

        base = sub.name.replace(".submission.json", "")
        receipt = receipts_dir / f"{base}.receipt.json"
        if not receipt.exists():
            skipped.append({"submission": str(sub.relative_to(ROOT)), "reason": "missing receipt"})
            continue

        rec = read_json(receipt)
        if rec.get("accepted") is not True:
            skipped.append({"submission": str(sub.relative_to(ROOT)), "reason": "receipt not accepted"})
            continue

        receipt_id = rec.get("receipt_id")
        if receipt_id in existing:
            skipped.append({"submission": str(sub.relative_to(ROOT)), "reason": "already finalized", "receipt_id": receipt_id})
            continue

        if args.mode == "live":
            run([
                sys.executable,
                "scripts/finalize_mainnet_prelaunch_record_from_submission.py",
                "--submission-json", str(sub.relative_to(ROOT)),
                "--receipt-json", str(receipt.relative_to(ROOT)),
                "--source-run-id", args.source_run_id,
                "--confirm-mainnet-prelaunch-append", confirm,
            ])
            run([sys.executable, "scripts/trinity_record_chain.py", "verify"])
            run([
                sys.executable,
                "scripts/verify_record_chain_integrity.py",
                "--ledger", "record-chain/hash-chain/main.chain.jsonl",
                "--head", "api/record-chain-head.json",
                "--chain-id", "trinity-record-chain-main",
                "--verify-payload-files",
                "--base-dir", ".",
            ])
            existing = existing_receipt_ids()

        finalized.append({"submission": str(sub.relative_to(ROOT)), "receipt_id": receipt_id})

    result = "pass"
    exit_code = 0
    if args.require_new_records and len(finalized) == 0:
        result = "fail"
        exit_code = 1

    print(json.dumps({
        "result": result,
        "mode": args.mode,
        "finalized_count": len(finalized),
        "skipped_count": len(skipped),
        "finalized": finalized,
        "skipped": skipped,
    }, indent=2, sort_keys=True))
    return exit_code

if __name__ == "__main__":
    raise SystemExit(main())
