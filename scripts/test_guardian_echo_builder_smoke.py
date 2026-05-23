#!/usr/bin/env python3
"""Smoke test: build_guardian_echo_payload.py succeeds with Guardian identity in title.

Verifies that the Guardian echo builder can process a title containing
"Guardian 00002" without being blocked by the pure echo builder's
unproofed-Guardian-identity check.  The wrapper passes
--allow-unproofed-guardian-mention to the base builder, then attaches
guardian_presence_proof and validates the result.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def generate_test_keypair(tmp: Path) -> tuple[Path, Path]:
    """Generate a temporary Ed25519 keypair using openssl."""
    priv = tmp / "test-guardian.private.pem"
    pub = tmp / "test-guardian.public.pem"
    subprocess.run(
        ["openssl", "genpkey", "-algorithm", "ed25519", "-out", str(priv)],
        check=True, capture_output=True, text=True,
    )
    subprocess.run(
        ["openssl", "pkey", "-in", str(priv), "-pubout", "-out", str(pub)],
        check=True, capture_output=True, text=True,
    )
    return priv, pub


def compute_pubkey_sha256(pub_path: Path) -> str:
    """Compute SHA-256 of the PEM public key content."""
    import hashlib
    content = pub_path.read_text(encoding="utf-8").strip() + "\n"
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def derive_guardian_id(pub_sha: str) -> str:
    """Derive guardian_id the same way attach_guardian_presence_proof.mjs does."""
    return "guardian_ed25519_" + pub_sha[:16]


def build_test_registry(tmp: Path, pub_sha: str, guardian_id: str) -> Path:
    """Create a minimal test guardian registry JSON."""
    registry = {
        "guardians": [
            {
                "guardian_registry_number": "00099",
                "guardian_id": guardian_id,
                "public_key_sha256": pub_sha,
                "algorithm": "ed25519",
                "status": "active",
                "guardian_type": "test",
                "label": "Smoke Test Guardian",
            }
        ]
    }
    path = tmp / "test-guardian-registry.json"
    path.write_text(json.dumps(registry, indent=2), encoding="utf-8")
    return path


def main() -> None:
    tmp = Path(tempfile.mkdtemp())

    # Generate keys
    priv, pub = generate_test_keypair(tmp)
    pub_sha = compute_pubkey_sha256(pub)
    guardian_id = derive_guardian_id(pub_sha)
    registry = build_test_registry(tmp, pub_sha, guardian_id)

    # Body file
    body = tmp / "body.md"
    body.write_text(
        "This is a read-oriented echo only, not authority, not attestation, "
        "not amendment, and not verification. Bitcoin Originals remain final. "
        "The agent reports only what it actually read and understood.",
        encoding="utf-8",
    )

    out = tmp / "guardian-echo-payload.json"
    key_prefix = str(tmp / "test-guardian")

    # Run the Guardian echo builder — title contains "Guardian 00099"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_guardian_echo_payload.py"),
            "--guardian-registry-number", "00099",
            "--guardian-id", guardian_id,
            "--guardian-key-prefix", key_prefix,
            "--echo-type", "E1_read_oriented_echo",
            "--title", "E1 Read-Oriented Echo — Guardian 00099",
            "--body-file", str(body),
            "--registry-path", str(registry),
            "--out", str(out),
        ],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    # Must succeed
    if result.returncode != 0:
        print("STDOUT:", result.stdout, file=sys.stderr)
        print("STDERR:", result.stderr, file=sys.stderr)
        raise AssertionError(
            f"build_guardian_echo_payload.py failed with exit code {result.returncode}"
        )

    # Output must exist and be valid JSON
    assert out.exists(), f"Output file not found: {out}"
    payload = json.loads(out.read_text(encoding="utf-8"))

    # Must have guardian_presence_proof
    proof = payload.get("guardian_presence_proof") or {}
    assert proof.get("guardian_id") == guardian_id, (
        f"guardian_id mismatch: expected {guardian_id}, got {proof.get('guardian_id')}"
    )
    assert proof.get("public_key_sha256") == pub_sha, (
        f"public_key_sha256 mismatch: expected {pub_sha}, got {proof.get('public_key_sha256')}"
    )

    # Title must be preserved (not silently replaced)
    assert "Guardian 00099" in payload.get("title", ""), (
        f"Title should contain 'Guardian 00099', got: {payload.get('title')}"
    )

    # Must be echo_candidate
    assert payload.get("submission_type") == "echo_candidate"
    assert payload.get("requested_archive_kind") == "agent_declared_echo_archive"

    print("PASS: test_guardian_echo_builder_smoke")
    print(f"  guardian_id: {guardian_id}")
    print(f"  public_key_sha256: {pub_sha[:16]}...")
    print(f"  payload title: {payload.get('title')}")


if __name__ == "__main__":
    main()
