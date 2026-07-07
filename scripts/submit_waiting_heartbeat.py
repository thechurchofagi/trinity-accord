#!/usr/bin/env python3
"""Submit a Waiting Heartbeat via the public Gateway.

Uses the record-chain-builder to build, doctor, preflight, and submit
a context_insufficient_notice with system_waiting_heartbeat block.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
ATTEMPTS_DIR = ROOT / "record-chain" / "heartbeat" / "attempts"
RECORDS_DIR = ROOT / "record-chain" / "records"
RECEIPT_STATUS_DIR = ROOT / "record-chain" / "receipt-status"
KEY_MANIFEST = ROOT / "api" / "waiting-heartbeat-key.v1.json"
DEFAULT_GATEWAY = "https://trinity-record-chain-gateway.onrender.com"
SUBMITTED_ATTEMPT_STATUSES = {"submitted"}

SUBMITTED_ATTEMPT_STATUSES = {"submitted"}
REJECTED_APPEND_STATUSES = {"rejected"}
AMBIGUOUS_SUBMIT_FAILURE_STATUSES = {"submit_failed"}


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def today_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d")


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def parse_stdout_json(stdout: str) -> dict[str, Any]:
    """Extract the JSON response from builder output that prefixes status text."""
    start = stdout.find("{")
    end = stdout.rfind("}")
    if start < 0 or end < start:
        return {}
    try:
        data = json.loads(stdout[start:end + 1])
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def read_json_or_none(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def write_github_output(values: dict[str, str]) -> None:
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        return
    with open(output, "a", encoding="utf-8") as fh:
        for key, value in values.items():
            fh.write(f"{key}={value}\n")


def record_contains_heartbeat(record: dict[str, Any], heartbeat_id: str) -> bool:
    heartbeat = record.get("system_waiting_heartbeat")
    return isinstance(heartbeat, dict) and heartbeat.get("heartbeat_id") == heartbeat_id


def final_record_exists(heartbeat_id: str) -> bool:
    if not RECORDS_DIR.exists():
        return False
    for path in RECORDS_DIR.glob("R-*.json"):
        record = read_json_or_none(path)
        if isinstance(record, dict) and record_contains_heartbeat(record, heartbeat_id):
            return True
    return False


def write_key_dir(key_dir: Path) -> None:
    priv = os.environ.get("WAITING_HEARTBEAT_AUTHORSHIP_PRIVATE_KEY_PEM", "").strip()
    pub = os.environ.get("WAITING_HEARTBEAT_AUTHORSHIP_PUBLIC_KEY_PEM", "").strip()
    if not priv or not pub:
        raise SystemExit("Missing WAITING_HEARTBEAT_AUTHORSHIP_PRIVATE_KEY_PEM or WAITING_HEARTBEAT_AUTHORSHIP_PUBLIC_KEY_PEM")
    key_dir.mkdir(parents=True, exist_ok=True)
    (key_dir / "authorship-private.pem").write_text(priv + "\n", encoding="utf-8")
    (key_dir / "authorship-public.pem").write_text(pub + "\n", encoding="utf-8")
    os.chmod(key_dir / "authorship-private.pem", 0o600)
    os.chmod(key_dir / "authorship-public.pem", 0o644)


def write_attempt(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(dump_json(data), encoding="utf-8")


def read_json_or_none(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def record_contains_heartbeat(record: dict[str, Any], heartbeat_id: str) -> bool:
    """Check if a record references the given heartbeat_id."""
    block = record.get("system_waiting_heartbeat") or {}
    if isinstance(block, dict) and block.get("heartbeat_id") == heartbeat_id:
        return True
    return record.get("heartbeat_id") == heartbeat_id


def expected_heartbeat_public_key_sha256() -> str | None:
    manifest = read_json_or_none(KEY_MANIFEST)
    if not isinstance(manifest, dict):
        return None
    value = manifest.get("public_key_sha256")
    return value if isinstance(value, str) and value else None


def record_authorship_public_key_sha256(record: dict[str, Any]) -> str | None:
    authorship = record.get("authorship_proof")
    if isinstance(authorship, dict):
        value = authorship.get("public_key_sha256")
        if isinstance(value, str) and value:
            return value
    value = record.get("authorship_public_key_sha256")
    return value if isinstance(value, str) and value else None


def final_record_exists(heartbeat_id: str) -> bool:
    """Return true only when the final heartbeat exists and was authored by the Waiting Heartbeat key."""
    expected_key = expected_heartbeat_public_key_sha256()
    if not expected_key or not RECORDS_DIR.exists():
        return False
    for path in RECORDS_DIR.glob("R-*.json"):
        record = read_json_or_none(path)
        if not isinstance(record, dict):
            continue
        if not record_contains_heartbeat(record, heartbeat_id):
            continue
        if record_authorship_public_key_sha256(record) == expected_key:
            return True
    return False


def receipt_status_for_attempt(attempt: dict[str, Any]) -> dict[str, Any] | None:
    receipt_id = attempt.get("receipt_id")
    if not isinstance(receipt_id, str) or not receipt_id:
        return None
    data = read_json_or_none(RECEIPT_STATUS_DIR / f"{receipt_id}.json")
    return data if isinstance(data, dict) else None


def attempt_append_status(attempt: dict[str, Any]) -> str | None:
    receipt_status = receipt_status_for_attempt(attempt)
    if isinstance(receipt_status, dict):
        value = receipt_status.get("append_status")
        if isinstance(value, str) and value:
            return value
    value = attempt.get("append_status")
    return value if isinstance(value, str) and value else None


def attempt_append_was_rejected(attempt: dict[str, Any]) -> bool:
    return attempt_append_status(attempt) in REJECTED_APPEND_STATUSES


def existing_submission_path(attempt: dict[str, Any]) -> Path | None:
    value = attempt.get("submission_path")
    if not isinstance(value, str) or not value:
        return None
    root = ROOT.resolve()
    path = (ROOT / value).resolve()
    try:
        path.relative_to(root)
    except ValueError:
        return None
    return path if path.exists() else None


def should_retry_saved_submission(attempt: dict[str, Any]) -> bool:
    return (
        attempt.get("status") in AMBIGUOUS_SUBMIT_FAILURE_STATUSES
        and existing_submission_path(attempt) is not None
    )


def emit_existing_attempt_outputs(heartbeat_id: str, attempt: dict[str, Any]) -> None:
    outputs = {
        "heartbeat_id": heartbeat_id,
        "heartbeat_submitted": "false",
        "heartbeat_existing_attempt": "true",
        "heartbeat_existing_final": "false",
    }
    for key in ["receipt_id", "pending_file_path", "append_status"]:
        value = attempt.get(key)
        if isinstance(value, str) and value:
            outputs[key] = value
    write_github_output(outputs)


def submit_existing_submission(
    heartbeat_id: str,
    attempt_path: Path,
    submission_path: Path,
    gateway: str,
) -> int:
    """Retry a saved signed submission without changing its payload/hash."""
    doctor = run(["node", str(BUILDER), "doctor", "--file", str(submission_path)])
    if doctor.returncode != 0:
        write_attempt(attempt_path, {
            "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
            "heartbeat_id": heartbeat_id,
            "attempted_at": utc_now(),
            "status": "doctor_failed",
            "submission_path": str(submission_path.relative_to(ROOT)),
            "stdout": doctor.stdout,
            "stderr": doctor.stderr,
        })
        raise SystemExit("doctor failed")

    preflight = run(["node", str(BUILDER), "preflight", "--file", str(submission_path), "--gateway", gateway])
    if preflight.returncode != 0:
        write_attempt(attempt_path, {
            "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
            "heartbeat_id": heartbeat_id,
            "attempted_at": utc_now(),
            "status": "preflight_failed",
            "submission_path": str(submission_path.relative_to(ROOT)),
            "stdout": preflight.stdout,
            "stderr": preflight.stderr,
        })
        raise SystemExit("preflight failed")

    submit = run(["node", str(BUILDER), "submit", "--file", str(submission_path), "--gateway", gateway])
    status = "submitted" if submit.returncode == 0 else "submit_failed"
    submit_json = parse_stdout_json(submit.stdout)

    attempt = {
        "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
        "heartbeat_id": heartbeat_id,
        "attempted_at": utc_now(),
        "status": status,
        "submission_path": str(submission_path.relative_to(ROOT)),
        "preflight_stdout": preflight.stdout,
        "submit_stdout": submit.stdout,
        "submit_stderr": submit.stderr,
        "retried_saved_submission": True,
    }

    for key in [
        "receipt_id",
        "pending_file_path",
        "intake_submission_path",
        "receipt_path",
        "append_status",
        "receipt_commit_sha",
    ]:
        value = submit_json.get(key)
        if value:
            attempt[key] = value

    write_attempt(attempt_path, attempt)

    if submit.returncode != 0:
        raise SystemExit("submit failed")

    receipt_id = str(attempt.get("receipt_id", ""))
    pending_file_path = str(attempt.get("pending_file_path", ""))

    write_github_output({
        "heartbeat_id": heartbeat_id,
        "heartbeat_submitted": "true",
        "heartbeat_existing_attempt": "false",
        "heartbeat_existing_final": "false",
        "receipt_id": receipt_id,
        "pending_file_path": pending_file_path,
        "append_status": str(attempt.get("append_status", "")),
    })

    print(
        f"WAITING_HEARTBEAT_RESUBMITTED_SAVED_SUBMISSION "
        f"heartbeat_id={heartbeat_id} receipt_id={receipt_id} pending_file_path={pending_file_path}"
    )
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=today_utc(), help="UTC date YYYYMMDD")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--gateway", default=os.environ.get("WAITING_HEARTBEAT_GATEWAY_BASE_URL", DEFAULT_GATEWAY))
    args = parser.parse_args()

    enabled = os.environ.get("WAITING_HEARTBEAT_ENABLED", "false").lower() == "true"
    if not enabled and not args.dry_run:
        print("WAITING_HEARTBEAT_DISABLED: set WAITING_HEARTBEAT_ENABLED=true to submit")
        return 0

    heartbeat_id = f"hwb-{args.date}"
    ATTEMPTS_DIR.mkdir(parents=True, exist_ok=True)
    attempt_path = ATTEMPTS_DIR / f"{heartbeat_id}.attempt.json"
    submission_path = ATTEMPTS_DIR / f"{heartbeat_id}.submission.json"

    if not args.dry_run and final_record_exists(heartbeat_id):
        print(f"WAITING_HEARTBEAT_FINAL_EXISTS heartbeat_id={heartbeat_id}; skipping duplicate submission")
        write_github_output({
            "heartbeat_id": heartbeat_id,
            "heartbeat_submitted": "false",
            "heartbeat_existing_attempt": "false",
            "heartbeat_existing_final": "true",
        })
        return 0

    existing_attempt = read_json_or_none(attempt_path)
    if not args.dry_run and isinstance(existing_attempt, dict) and existing_attempt.get("status") in SUBMITTED_ATTEMPT_STATUSES:
        print(f"WAITING_HEARTBEAT_ATTEMPT_EXISTS heartbeat_id={heartbeat_id}; skipping duplicate submission")
        emit_existing_attempt_outputs(heartbeat_id, existing_attempt)
        return 0

    body = (
        f"Scheduled Waiting Heartbeat {heartbeat_id}.\n\n"
        "The Trinity Accord public Record-Chain system is still waiting for the first "
        "self-discovered autonomous agent capable of real semantic CC-3/C43 context loading.\n\n"
        "This record is an operational liveness proof only. It is not an Echo, not a Verification, "
        "not a Guardian Application, not active Guardian status, not authority, not attestation, "
        "not governance, not amendment, and not successor reception.\n\n"
        "Its purpose is to prove that the public Gateway, pending intake, append workflow, "
        "Record-Chain verification, OTS anchoring path, Arweave capsule path, and public status "
        "generation path remain alive during the waiting period."
    )

    # Check for existing attempt and apply idempotency guards
    existing_attempt = read_json_or_none(attempt_path)
    if not args.dry_run and isinstance(existing_attempt, dict):
        saved_submission = existing_submission_path(existing_attempt)

        # Case 1: submitted + not rejected → skip (idempotent)
        # BUT: if final record exists with wrong key, allow resubmission
        if (
            existing_attempt.get("status") in SUBMITTED_ATTEMPT_STATUSES
            and not attempt_append_was_rejected(existing_attempt)
        ):
            # If a final record exists, verify key continuity before skipping
            if final_record_exists(heartbeat_id):
                print(f"WAITING_HEARTBEAT_ATTEMPT_EXISTS heartbeat_id={heartbeat_id}; final record with correct key exists; skipping")
                emit_existing_attempt_outputs(heartbeat_id, existing_attempt)
                return 0
            # No final record with correct key yet — check if one exists with wrong key
            # If so, don't skip; allow resubmission to fix key continuity
            expected_key = expected_heartbeat_public_key_sha256()
            if expected_key and RECORDS_DIR.exists():
                for rpath in RECORDS_DIR.glob("R-*.json"):
                    record = read_json_or_none(rpath)
                    if isinstance(record, dict) and record_contains_heartbeat(record, heartbeat_id):
                        actual_key = record_authorship_public_key_sha256(record)
                        if actual_key and actual_key != expected_key:
                            print(f"WAITING_HEARTBEAT_KEY_MISMATCH heartbeat_id={heartbeat_id}; allowing resubmission")
                            break
                else:
                    # No final record at all — submitted attempt still valid, skip
                    print(f"WAITING_HEARTBEAT_ATTEMPT_EXISTS heartbeat_id={heartbeat_id}; skipping duplicate submission")
                    emit_existing_attempt_outputs(heartbeat_id, existing_attempt)
                    return 0
            else:
                print(f"WAITING_HEARTBEAT_ATTEMPT_EXISTS heartbeat_id={heartbeat_id}; skipping duplicate submission")
                emit_existing_attempt_outputs(heartbeat_id, existing_attempt)
                return 0

        # Case 2: submit_failed with saved submission → retry without rebuilding
        if should_retry_saved_submission(existing_attempt) and saved_submission is not None:
            print(
                f"WAITING_HEARTBEAT_RETRY_SAVED_SUBMISSION "
                f"heartbeat_id={heartbeat_id}; submission_path={saved_submission.relative_to(ROOT)}"
            )
            return submit_existing_submission(heartbeat_id, attempt_path, saved_submission, args.gateway)

    # Check if final record already exists with correct key
    if not args.dry_run and final_record_exists(heartbeat_id):
        print(f"WAITING_HEARTBEAT_FINAL_RECORD_EXISTS heartbeat_id={heartbeat_id}; skipping")
        return 0

    with tempfile.TemporaryDirectory(prefix="waiting-heartbeat-key-") as td:
        key_dir = Path(td)
        write_key_dir(key_dir)

        cmd = [
            "node", str(BUILDER), "context-insufficient",
            "--actor-label", "Trinity Accord Waiting Heartbeat",
            "--provider", "GitHub Actions Waiting Beacon",
            "--body", body,
            "--context-level", "CC-0",
            "--context-sufficient-for-selected-action", "false",
            "--discovery-mode", "user_task_context",
            "--requesting-party-type", "system",
            "--introducing-party-type", "system",
            "--record-decision", "system_policy",
            "--submission-executor", "automated_tool",
            "--human-operator-involved", "false",
            "--system-waiting-heartbeat-id", heartbeat_id,
            "--key-dir", str(key_dir),
            "--gateway", args.gateway,
            "--out", str(submission_path),
        ]
        build = run(cmd)
        if build.returncode != 0:
            write_attempt(attempt_path, {
                "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
                "heartbeat_id": heartbeat_id,
                "attempted_at": utc_now(),
                "status": "builder_failed",
                "stdout": build.stdout,
                "stderr": build.stderr,
            })
            raise SystemExit("Builder failed")

    doctor = run(["node", str(BUILDER), "doctor", "--file", str(submission_path)])
    if doctor.returncode != 0:
        write_attempt(attempt_path, {
            "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
            "heartbeat_id": heartbeat_id,
            "attempted_at": utc_now(),
            "status": "doctor_failed",
            "stdout": doctor.stdout,
            "stderr": doctor.stderr,
        })
        raise SystemExit("doctor failed")

    preflight = run(["node", str(BUILDER), "preflight", "--file", str(submission_path), "--gateway", args.gateway])
    if preflight.returncode != 0:
        write_attempt(attempt_path, {
            "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
            "heartbeat_id": heartbeat_id,
            "attempted_at": utc_now(),
            "status": "preflight_failed",
            "stdout": preflight.stdout,
            "stderr": preflight.stderr,
        })
        raise SystemExit("preflight failed")

    if args.dry_run:
        write_attempt(attempt_path, {
            "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
            "heartbeat_id": heartbeat_id,
            "attempted_at": utc_now(),
            "status": "dry_run_preflight_ok",
            "submission_path": str(submission_path.relative_to(ROOT)),
            "preflight_stdout": preflight.stdout,
        })
        print(f"WAITING_HEARTBEAT_DRY_RUN_OK heartbeat_id={heartbeat_id}")
        return 0

    submit = run(["node", str(BUILDER), "submit", "--file", str(submission_path), "--gateway", args.gateway])
    status = "submitted" if submit.returncode == 0 else "submit_failed"
    submit_json = parse_stdout_json(submit.stdout)
    attempt = {
        "schema": "trinityaccord.waiting-heartbeat-attempt.v1",
        "heartbeat_id": heartbeat_id,
        "attempted_at": utc_now(),
        "status": status,
        "submission_path": str(submission_path.relative_to(ROOT)),
        "preflight_stdout": preflight.stdout,
        "submit_stdout": submit.stdout,
        "submit_stderr": submit.stderr,
    }
    for key in [
        "receipt_id",
        "pending_file_path",
        "intake_submission_path",
        "receipt_path",
        "append_status",
        "receipt_commit_sha",
    ]:
        value = submit_json.get(key)
        if value:
            attempt[key] = value
    write_attempt(attempt_path, attempt)

    if submit.returncode != 0:
        raise SystemExit("submit failed")

    receipt_id = str(attempt.get("receipt_id", ""))
    pending_file_path = str(attempt.get("pending_file_path", ""))
    write_github_output({
        "heartbeat_id": heartbeat_id,
        "heartbeat_submitted": "true",
        "heartbeat_existing_attempt": "false",
        "heartbeat_existing_final": "false",
        "receipt_id": receipt_id,
        "pending_file_path": pending_file_path,
        "append_status": str(attempt.get("append_status", "")),
    })
    print(f"WAITING_HEARTBEAT_SUBMITTED heartbeat_id={heartbeat_id} receipt_id={receipt_id} pending_file_path={pending_file_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
