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

def receipt_id_from_receipt(receipt: dict[str, Any]) -> str:
    """Return canonical receipt id across legacy and server receipt schemas."""
    rid = receipt.get("receipt_id") or receipt.get("server_receipt_id")
    return str(rid or "")


def receipt_is_accepted(receipt: dict[str, Any]) -> bool:
    """Accept both legacy accepted receipts and immutable server receipts."""
    return receipt.get("accepted") is True or bool(receipt.get("server_receipt_id"))


def iter_submission_paths(submissions_dir: Path) -> list[Path]:
    """Find dated and legacy intake submission files deterministically."""
    return sorted(submissions_dir.glob("**/*.submission.json"))


def find_receipt_for_submission(submission_path: Path, submissions_dir: Path, receipts_dir: Path) -> Path:
    """Map submissions/YYYY/MM/<id>.submission.json to receipts/YYYY/MM/<id>.receipt.json."""
    rel = submission_path.relative_to(submissions_dir)
    return receipts_dir / str(rel).replace(".submission.json", ".receipt.json")


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
    ap.add_argument("--submissions-dir", default="record-chain/intake/submissions")
    ap.add_argument("--receipts-dir", default="record-chain/intake/receipts")
    ap.add_argument("--max-records", type=int, default=10)
    ap.add_argument("--source-run-id", default="auto-finalize")
    ap.add_argument("--mode", choices=["dry-run", "live"], default="dry-run")
    args = ap.parse_args()

    submissions_dir = ROOT / args.submissions_dir
    receipts_dir = ROOT / args.receipts_dir

    if not submissions_dir.exists() or not receipts_dir.exists():
        print(json.dumps({
            "result": "pass",
            "mode": args.mode,
            "finalized_count": 0,
            "skipped_count": 0,
            "reason": "intake directories missing; no-op"
        }, indent=2, sort_keys=True))
        return 0

    existing = existing_receipt_ids()
    finalized = []
    skipped = []

    confirm = current_confirm_string()

    for sub in iter_submission_paths(submissions_dir):
        if len(finalized) >= args.max_records:
            break

        receipt = find_receipt_for_submission(sub, submissions_dir, receipts_dir)
        if not receipt.exists():
            skipped.append({"submission": str(sub.relative_to(ROOT)), "reason": "missing receipt"})
            continue

        rec = read_json(receipt)
        if not receipt_is_accepted(rec):
            skipped.append({"submission": str(sub.relative_to(ROOT)), "reason": "receipt not accepted"})
            continue

        receipt_id = receipt_id_from_receipt(rec)
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

    print(json.dumps({
        "result": "pass",
        "mode": args.mode,
        "finalized_count": len(finalized),
        "skipped_count": len(skipped),
        "finalized": finalized,
        "skipped": skipped,
    }, indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
