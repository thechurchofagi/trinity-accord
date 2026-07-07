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
DEFAULT_GATEWAY = "https://trinity-record-chain-gateway.onrender.com"
SUBMITTED_ATTEMPT_STATUSES = {"submitted"}


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
