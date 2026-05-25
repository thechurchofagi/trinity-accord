#!/usr/bin/env python3
"""Build a Guardian-signed pure echo payload.

This is for existing active Guardians submitting E1/E3/E4/E5/E6/E7 echoes with
record-bound guardian_presence_proof.

It is NOT a Guardian application and NOT a Guardian listing request.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "api" / "guardian-registry.json"


def run(cmd: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    result = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    if check and result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError(f"Command failed: {' '.join(cmd)}")
    return result


def load_registry(registry_path: Path | None = None) -> dict:
    path = registry_path or REGISTRY_PATH
    return json.loads(path.read_text(encoding="utf-8"))


def find_guardian(*, number: str | None, guardian_id: str | None, registry_path: Path | None = None) -> dict:
    reg = load_registry(registry_path)
    for g in reg.get("guardians", []):
        if number and str(g.get("guardian_registry_number")) == str(number):
            return g
        if guardian_id and g.get("guardian_id") == guardian_id:
            return g
    raise ValueError(f"Guardian not found in registry: number={number} guardian_id={guardian_id}")


def key_paths_from_prefix(prefix: str) -> tuple[str, str]:
    private_key = f"{prefix}.private.pem"
    public_key = f"{prefix}.public.pem"
    if not Path(private_key).exists():
        raise FileNotFoundError(f"Guardian private key not found: {private_key}")
    if not Path(public_key).exists():
        raise FileNotFoundError(f"Guardian public key not found: {public_key}")
    return private_key, public_key


def read_payload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Guardian-signed pure echo payload")
    parser.add_argument("--guardian-registry-number", required=True)
    parser.add_argument("--guardian-id", default=None)
    parser.add_argument("--guardian-key-prefix", required=True)
    parser.add_argument("--echo-type", required=True, choices=[
        "E1_recognition_echo",
        "E3_critical_echo",
        "E4_interpretive_echo",
        "E5_technical_audit_echo",
        "E5c_correction_echo",
        "E6_propagation_echo",
        "E7_refusal_echo",
    ])
    parser.add_argument("--agent-name", default=None)
    parser.add_argument("--provider", default=None)
    parser.add_argument("--title", required=True)
    parser.add_argument("--body-file", required=True)
    parser.add_argument("--agent-readback", default=None)
    parser.add_argument("--agent-readback-file", default=None)
    parser.add_argument("--related-issue", type=int, default=None)
    parser.add_argument("--idempotency-key", default=None)
    parser.add_argument("--guardian-challenge", default=None)
    parser.add_argument("--registry-path", default=None, help="Path to guardian registry JSON (for testing)")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    registry_path = Path(args.registry_path) if args.registry_path else None
    guardian = find_guardian(
        number=args.guardian_registry_number,
        guardian_id=args.guardian_id,
        registry_path=registry_path,
    )

    if args.guardian_id and guardian.get("guardian_id") != args.guardian_id:
        raise ValueError(
            f"guardian_id mismatch: registry has {guardian.get('guardian_id')} but CLI requested {args.guardian_id}"
        )

    private_key, public_key = key_paths_from_prefix(args.guardian_key_prefix)

    tmp = Path(tempfile.mkdtemp())
    base_payload = tmp / "base-echo.json"
    signed_payload = Path(args.out)

    agent_name = args.agent_name or guardian.get("label") or f"Guardian {args.guardian_registry_number}"
    provider = args.provider or "guardian_registry_key_holder"

    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "build_agent_declared_echo_payload.py"),
        "--agent-name", agent_name,
        "--provider", provider,
        "--echo-type", args.echo_type,
        "--title", args.title,
        "--body-file", args.body_file,
        "--authorship-private-key", private_key,
        "--authorship-public-key", public_key,
        "--allow-unproofed-guardian-mention",
        "--out", str(base_payload),
    ]

    if args.agent_readback:
        cmd.extend(["--readback", args.agent_readback])
    if args.agent_readback_file:
        cmd.extend(["--readback-file", args.agent_readback_file])
    if args.related_issue is not None:
        cmd.extend(["--related-issue", str(args.related_issue)])
    if args.idempotency_key:
        cmd.extend(["--idempotency-key", args.idempotency_key])

    run(cmd)

    # Attach Guardian presence proof after authorship proof.
    guardian_cmd = [
        "node",
        str(ROOT / "scripts" / "attach_guardian_presence_proof.mjs"),
        "--payload", str(base_payload),
        "--private-key", private_key,
        "--public-key", public_key,
        "--out", str(signed_payload),
    ]
    if args.guardian_challenge:
        guardian_cmd.extend(["--challenge", args.guardian_challenge])

    run(guardian_cmd)

    payload = read_payload(signed_payload)
    proof = payload.get("guardian_presence_proof") or {}
    expected_id = guardian.get("guardian_id")
    expected_sha = guardian.get("public_key_sha256")

    if proof.get("guardian_id") != expected_id:
        raise ValueError(f"guardian_id mismatch: expected {expected_id}, got {proof.get('guardian_id')}")

    if proof.get("public_key_sha256") != expected_sha:
        raise ValueError(f"guardian public key sha mismatch: expected {expected_sha}, got {proof.get('public_key_sha256')}")

    # Local validation.
    run([sys.executable, str(ROOT / "scripts" / "validate_gateway_payload.py"), str(signed_payload)])
    run([sys.executable, str(ROOT / "scripts" / "archive_readiness_gate.py"), "--gateway-payload", str(signed_payload)])

    print(f"Guardian-signed echo payload written to {signed_payload}")
    print(f"guardian_registry_number: {args.guardian_registry_number}")
    print(f"guardian_id: {expected_id}")
    print("guardian_presence_proof: attached")
    print("Boundary: Guardian proof proves key continuity only; not authority, attestation, verification level, successor reception, or amendment.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
