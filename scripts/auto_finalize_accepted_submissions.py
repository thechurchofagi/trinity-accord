#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
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

def stable_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(stable_json(obj).encode("utf-8")).hexdigest()

def compute_receipt_sha256(receipt: dict[str, Any]) -> str:
    material = dict(receipt)
    material.pop("receipt_sha256", None)
    return sha256_obj(material)

def assert_receipt_binds_submission(
    submission: dict[str, Any],
    receipt: dict[str, Any],
    submission_path: Path,
    receipt_path: Path,
) -> None:
    rel_submission = str(submission_path.relative_to(ROOT))
    rel_receipt = str(receipt_path.relative_to(ROOT))

    if receipt.get("intake_submission_path") != rel_submission:
        raise ValueError("receipt intake_submission_path mismatch")
    if receipt.get("receipt_path") != rel_receipt:
        raise ValueError("receipt receipt_path mismatch")
    if receipt.get("stored_submission_sha256") != sha256_obj(submission):
        raise ValueError("receipt stored_submission_sha256 mismatch")
    if receipt.get("receipt_sha256") != compute_receipt_sha256(receipt):
        raise ValueError("receipt_sha256 mismatch")

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


def pending_path_from_receipt(receipt: dict) -> Path | None:
    """Return the repository path for the Gateway pending file bound to a receipt."""
    raw = receipt.get("pending_file_path")
    if not isinstance(raw, str) or not raw.strip():
        return None
    return ROOT / raw


def native_artifact_path_for_pending(pending_path: Path, directory: str) -> Path:
    """Map record-chain/pending/<name>.json to record-chain/<directory>/<name>.json."""
    return ROOT / "record-chain" / directory / pending_path.name


def native_pending_artifact_status(receipt: dict) -> tuple[str, str]:
    """Return native processing state for the pending file bound to a receipt.

    States:
    - none: no native pending/processed/rejected artifact was found.
    - pending: Gateway pending still exists and must be consumed by append workflow.
    - processed: pending was consumed into native record-chain.
    - rejected: pending was rejected by native append and must not be finalized blindly.
    - no_pending_path: older receipt shape without pending_file_path; leave legacy behavior.
    """
    pending_path = pending_path_from_receipt(receipt)
    if pending_path is None:
        return "no_pending_path", "receipt has no pending_file_path"

    if pending_path.exists():
        return "pending", f"native pending still queued: {pending_path.relative_to(ROOT)}"

    processed_path = native_artifact_path_for_pending(pending_path, "processed")
    if processed_path.exists():
        return "processed", f"native pending already processed: {processed_path.relative_to(ROOT)}"

    rejected_path = native_artifact_path_for_pending(pending_path, "rejected")
    if rejected_path.exists():
        return "rejected", f"native pending already rejected: {rejected_path.relative_to(ROOT)}"

    return "none", "native pending artifact not found"

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

        submission_obj = read_json(sub)
        try:
            assert_receipt_binds_submission(submission_obj, rec, sub, receipt)
        except ValueError as exc:
            skipped.append({
                "submission": str(sub.relative_to(ROOT)),
                "receipt": str(receipt.relative_to(ROOT)),
                "reason": "receipt_submission_binding_mismatch",
                "detail": str(exc),
            })
            continue

        receipt_id = receipt_id_from_receipt(rec)
        if receipt_id in existing:
            skipped.append({"submission": str(sub.relative_to(ROOT)), "reason": "already finalized", "receipt_id": receipt_id})
            continue

        native_state, native_detail = native_pending_artifact_status(rec)
        if native_state in {"pending", "processed", "rejected"}:
            skipped.append({
                "submission": str(sub.relative_to(ROOT)),
                "receipt": str(receipt.relative_to(ROOT)),
                "reason": f"native_pending_{native_state}",
                "detail": native_detail,
                "receipt_id": receipt_id,
            })
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
