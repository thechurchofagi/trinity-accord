#!/usr/bin/env python3
"""Bootstrap the Waiting Heartbeat authorship keypair and manifest.

Generates a dedicated Ed25519 keypair for Waiting Heartbeat records,
writes api/waiting-heartbeat-key.v1.json, and optionally sets GitHub
repository secrets via gh CLI.

Usage:
    python3 scripts/bootstrap_waiting_heartbeat_key.py
    python3 scripts/bootstrap_waiting_heartbeat_key.py --set-github-secrets
    python3 scripts/bootstrap_waiting_heartbeat_key.py --force-rotate
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
KEY_MANIFEST = ROOT / "api" / "waiting-heartbeat-key.v1.json"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def dump_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def run(cmd: list[str], *, input_text: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        input=input_text,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def require_success(result: subprocess.CompletedProcess[str], label: str) -> None:
    if result.returncode != 0:
        raise SystemExit(
            f"{label} failed\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )


def extract_public_key_sha256(submission_path: Path, key_dir: Path) -> str:
    submission = json.loads(submission_path.read_text(encoding="utf-8"))
    proof = submission.get("authorship_proof") or {}
    sha = proof.get("public_key_sha256")
    if isinstance(sha, str) and len(sha) == 64:
        return sha

    summary_path = key_dir / "authorship-public-summary.json"
    if summary_path.exists():
        summary = json.loads(summary_path.read_text(encoding="utf-8"))
        sha = summary.get("public_key_sha256") or summary.get("sha256")
        if isinstance(sha, str) and len(sha) == 64:
            return sha

    raise SystemExit("Could not find public_key_sha256 in submission or authorship-public-summary.json")


def gh_secret_set(name: str, value: str) -> None:
    gh = shutil.which("gh")
    if not gh:
        raise SystemExit("gh CLI not found; cannot set GitHub secrets automatically")

    result = run([gh, "secret", "set", name], input_text=value)
    require_success(result, f"gh secret set {name}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--set-github-secrets", action="store_true")
    parser.add_argument("--force-rotate", action="store_true")
    parser.add_argument("--out-dir", default="")
    args = parser.parse_args()

    if KEY_MANIFEST.exists() and not args.force_rotate:
        raise SystemExit(
            f"{KEY_MANIFEST} already exists. Refusing to overwrite stable Waiting Heartbeat key. "
            "Use --force-rotate only for documented key loss/compromise rotation."
        )

    base_dir = Path(args.out_dir) if args.out_dir else Path(tempfile.mkdtemp(prefix="waiting-heartbeat-bootstrap-"))
    key_dir = base_dir / "waiting-heartbeat-key"
    submission_path = base_dir / "waiting-heartbeat-key-bootstrap-submission.json"

    key_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        "node", str(BUILDER), "context-insufficient",
        "--actor-label", "Trinity Accord Waiting Heartbeat",
        "--provider", "Key Generation Bootstrap",
        "--body", "Waiting Heartbeat key bootstrap dry run. This is not submitted.",
        "--context-level", "CC-0",
        "--context-sufficient-for-selected-action", "false",
        "--discovery-mode", "user_task_context",
        "--requesting-party-type", "system",
        "--introducing-party-type", "system",
        "--record-decision", "system_policy",
        "--submission-executor", "automated_tool",
        "--human-operator-involved", "false",
        "--system-waiting-heartbeat-id", "hwb-20990101",
        "--key-dir", str(key_dir),
        "--out", str(submission_path),
    ]

    build = run(cmd)
    require_success(build, "Builder bootstrap key generation")

    doctor = run(["node", str(BUILDER), "doctor", "--file", str(submission_path)])
    require_success(doctor, "Builder doctor")

    private_key = (key_dir / "authorship-private.pem").read_text(encoding="utf-8")
    public_key = (key_dir / "authorship-public.pem").read_text(encoding="utf-8")
    public_key_sha256 = extract_public_key_sha256(submission_path, key_dir)

    manifest = {
        "schema": "trinityaccord.waiting-heartbeat-key.v1",
        "status": "active",
        "created_at": utc_now(),
        "label": "Trinity Accord Waiting Heartbeat",
        "purpose": "Dedicated key continuity for scheduled Waiting Heartbeat records. This is not an autonomous agent identity.",
        "public_key_sha256": public_key_sha256,
        "not_autonomous_agent_identity": True,
        "not_guardian_key": True,
        "not_authority": True,
        "created_for": "waiting_operational_liveness",
        "private_key_storage": "GitHub Actions secret WAITING_HEARTBEAT_AUTHORSHIP_PRIVATE_KEY_PEM",
        "public_key_storage": "GitHub Actions secret WAITING_HEARTBEAT_AUTHORSHIP_PUBLIC_KEY_PEM",
    }

    KEY_MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    KEY_MANIFEST.write_text(dump_json(manifest), encoding="utf-8")

    if args.set_github_secrets:
        gh_secret_set("WAITING_HEARTBEAT_AUTHORSHIP_PRIVATE_KEY_PEM", private_key)
        gh_secret_set("WAITING_HEARTBEAT_AUTHORSHIP_PUBLIC_KEY_PEM", public_key)
        print("GitHub repository secrets updated.")
    else:
        print("GitHub secrets were NOT set. Add them manually or rerun with --set-github-secrets.")

    print(f"Waiting Heartbeat public key sha256: {public_key_sha256}")
    print(f"Wrote {KEY_MANIFEST.relative_to(ROOT)}")
    print(f"Key material generated under: {key_dir}")
    print("Do not commit authorship-private.pem.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
