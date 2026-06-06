#!/usr/bin/env python3
"""Update post-M1 test progress ledger and write checkpoints.

Usage:
  python3 scripts/update_post_m1_test_progress.py \
    --phase M2 --step M2.1 --mode EXT --status in_progress \
    --summary "Starting external rehearsal." --resume-step M2.1 \
    --session-id run-001

All paths are relative to repo root.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROGRESS_PATH = os.path.join(
    REPO_ROOT, "record-chain", "testing", "post-m1-live-test", "progress.v1.json"
)
CHECKPOINT_DIR = os.path.join(
    REPO_ROOT, "record-chain", "testing", "post-m1-live-test", "checkpoints"
)

VALID_PHASES = ["P0", "M2", "M3", "M4", "M5", "M6", "M7", "M8", "M9"]
VALID_MODES = [
    "EXT", "INT-CHECKPOINT", "INT-DIAG", "INT-FIX", "INT-FINALIZE", "INT-ARCHIVE",
]
VALID_STATUSES = [
    "not_started", "in_progress", "pass", "fail", "blocked", "skipped",
]

PRIVATE_KEY_PATTERNS = [
    re.compile(r"BEGIN PRIVATE KEY", re.IGNORECASE),
    re.compile(r"BEGIN EC PRIVATE KEY", re.IGNORECASE),
    re.compile(r"BEGIN RSA PRIVATE KEY", re.IGNORECASE),
    re.compile(r"BEGIN OPENSSH PRIVATE KEY", re.IGNORECASE),
    re.compile(r"authorship-private\.pem"),
]

VOLATILE_PATH_PATTERNS = [
    re.compile(r"/root/\.openclaw"),
    re.compile(r"/mnt/data"),
    re.compile(r"/tmp/phase"),
    re.compile(r"/home/[^/]+/\.openclaw"),
]


def scan_for_secrets(text: str) -> list:
    found = []
    for pat in PRIVATE_KEY_PATTERNS:
        if pat.search(text):
            found.append(pat.pattern)
    return found


def scan_for_volatile_paths(text: str) -> list:
    found = []
    for pat in VOLATILE_PATH_PATTERNS:
        if pat.search(text):
            found.append(pat.pattern)
    return found


def validate_public_key_sha256(val: str) -> bool:
    return bool(re.match(r"^[0-9a-fA-F]{64}$", val))


def load_progress() -> dict:
    if not os.path.exists(PROGRESS_PATH):
        print(f"ERROR: progress.v1.json not found at {PROGRESS_PATH}", file=sys.stderr)
        sys.exit(1)
    with open(PROGRESS_PATH, "r") as f:
        return json.load(f)


def save_progress(data: dict):
    os.makedirs(os.path.dirname(PROGRESS_PATH), exist_ok=True)
    with open(PROGRESS_PATH, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def write_checkpoint(checkpoint_id: str, checkpoint_data: dict):
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    path = os.path.join(CHECKPOINT_DIR, f"{checkpoint_id}.json")
    with open(path, "w") as f:
        json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    return path


def main():
    parser = argparse.ArgumentParser(description="Update post-M1 test progress")
    parser.add_argument("--phase", required=True, choices=VALID_PHASES)
    parser.add_argument("--step", required=True)
    parser.add_argument("--mode", required=True, choices=VALID_MODES)
    parser.add_argument("--status", required=True, choices=VALID_STATUSES)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--resume-step", default=None)
    parser.add_argument("--marker", default=None)
    parser.add_argument("--receipt-id", default=None)
    parser.add_argument("--public-key-sha256", default=None)
    parser.add_argument("--anomaly-json", default=None)
    parser.add_argument("--stop-rule", default=None)
    parser.add_argument("--artifact-manifest", default=None)
    parser.add_argument("--session-id", default=None)
    parser.add_argument("--session-expires-minutes", type=int, default=35)

    args = parser.parse_args()

    # Validate no secrets in summary
    secret_matches = scan_for_secrets(args.summary)
    if secret_matches:
        print(f"ERROR: summary contains secret patterns: {secret_matches}", file=sys.stderr)
        sys.exit(1)

    # Validate no volatile paths in summary
    volatile_matches = scan_for_volatile_paths(args.summary)
    if volatile_matches:
        print(f"ERROR: summary contains volatile paths: {volatile_matches}", file=sys.stderr)
        sys.exit(1)

    # Validate public key if provided
    if args.public_key_sha256 and not validate_public_key_sha256(args.public_key_sha256):
        print("ERROR: public_key_sha256 must be 64 hex chars", file=sys.stderr)
        sys.exit(1)

    # Load progress
    progress = load_progress()
    now = datetime.datetime.utcnow().isoformat() + "Z"

    # Update progress fields
    progress["current_phase"] = args.phase
    progress["current_step"] = args.step
    progress["current_mode"] = args.mode
    progress["overall_status"] = args.status if args.status in ("pass", "fail") else progress["overall_status"]
    progress["updated_at"] = now

    if args.resume_step:
        progress["last_safe_resume_step"] = args.resume_step

    # Update phase status
    if args.phase in progress.get("phase_status", {}):
        progress["phase_status"][args.phase]["status"] = args.status
        if args.resume_step:
            progress["phase_status"][args.phase]["resume_step"] = args.resume_step
        if args.stop_rule:
            progress["phase_status"][args.phase]["blocking_issue"] = args.summary

    # Add marker
    if args.marker:
        markers = progress.get("completed_markers", [])
        if args.marker not in markers:
            markers.append(args.marker)
            progress["completed_markers"] = markers

    # Add receipt id
    if args.receipt_id:
        receipt_ids = progress.get("latest_external_receipt_ids", [])
        if args.receipt_id not in receipt_ids:
            receipt_ids.append(args.receipt_id)
            progress["latest_external_receipt_ids"] = receipt_ids

    # Update public key
    if args.public_key_sha256:
        progress["latest_external_public_key_sha256"] = args.public_key_sha256

    # Add anomaly
    if args.anomaly_json:
        try:
            anomaly = json.loads(args.anomaly_json)
        except json.JSONDecodeError:
            anomaly = {"raw": args.anomaly_json}
        anomalies = progress.get("known_anomalies", [])
        anomalies.append(anomaly)
        progress["known_anomalies"] = anomalies

    # Add stop rule
    if args.stop_rule:
        stop_rules = progress.get("stop_rules_triggered", [])
        if args.stop_rule not in stop_rules:
            stop_rules.append(args.stop_rule)
            progress["stop_rules_triggered"] = stop_rules

    # Update artifact manifest sha
    if args.artifact_manifest and os.path.exists(os.path.join(REPO_ROOT, args.artifact_manifest)):
        with open(os.path.join(REPO_ROOT, args.artifact_manifest), "rb") as f:
            sha = hashlib.sha256(f.read()).hexdigest()
        progress["latest_artifact_manifest_sha256"] = sha

    # Session management
    if args.session_id:
        expires = (
            datetime.datetime.utcnow()
            + datetime.timedelta(minutes=args.session_expires_minutes)
        ).isoformat() + "Z"
        progress["active_session"] = {
            "session_id": args.session_id,
            "mode": args.mode,
            "owner": "agent",
            "started_at": now,
            "updated_at": now,
            "expires_at": expires,
        }

    # Final secret scan on entire progress
    progress_text = json.dumps(progress)
    final_secrets = scan_for_secrets(progress_text)
    if final_secrets:
        print(f"ERROR: final progress contains secret patterns: {final_secrets}", file=sys.stderr)
        sys.exit(1)
    final_volatile = scan_for_volatile_paths(progress_text)
    if final_volatile:
        print(f"ERROR: final progress contains volatile paths: {final_volatile}", file=sys.stderr)
        sys.exit(1)

    # Save progress
    save_progress(progress)
    print(f"Progress updated: {args.phase} / {args.step} / {args.mode} / {args.status}")

    # Write checkpoint
    checkpoint_id = f"cp-{args.phase}-{args.step}-{datetime.datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}"
    checkpoint_data = {
        "checkpoint_id": checkpoint_id,
        "phase": args.phase,
        "step": args.step,
        "mode": args.mode,
        "status": args.status,
        "summary": args.summary,
        "resume_step": args.resume_step,
        "marker": args.marker,
        "receipt_id": args.receipt_id,
        "public_key_sha256": args.public_key_sha256,
        "session_id": args.session_id,
        "created_at": now,
    }
    cp_path = write_checkpoint(checkpoint_id, checkpoint_data)
    print(f"Checkpoint written: {cp_path}")


if __name__ == "__main__":
    main()
