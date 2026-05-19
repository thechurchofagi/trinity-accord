#!/usr/bin/env python3
"""Shared CLI helpers for attaching Gateway payload authorship proof.

Authorship proof is an optional final step for any Gateway payload. It proves
key continuity only. It does not change authority, verification, attestation,
reception, or amendment status.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ATTACH_SCRIPT = ROOT / "scripts" / "attach_agent_authorship_proof.mjs"


def add_authorship_arguments(parser):
    """Add optional authorship proof flags to a Gateway payload builder."""
    group = parser.add_argument_group(
        "optional authorship proof",
        "Attach an Ed25519 key-continuity proof to the final Gateway payload. "
        "This is optional and does not affect counts or verification level.",
    )
    group.add_argument(
        "--authorship-key-prefix",
        default=None,
        help=(
            "Prefix for an existing authorship keypair. The builder will use "
            "<prefix>.private.pem and <prefix>.public.pem."
        ),
    )
    group.add_argument(
        "--authorship-private-key",
        default=None,
        help="Path to existing Ed25519 private key PEM. Never submit this file.",
    )
    group.add_argument(
        "--authorship-public-key",
        default=None,
        help="Path to matching Ed25519 public key PEM.",
    )


def resolve_authorship_key_paths(args):
    """Return (private_key, public_key) paths or (None, None)."""
    prefix = getattr(args, "authorship_key_prefix", None)
    private_key = getattr(args, "authorship_private_key", None)
    public_key = getattr(args, "authorship_public_key", None)

    if prefix:
        if private_key or public_key:
            raise ValueError(
                "Use either --authorship-key-prefix or explicit --authorship-private-key/--authorship-public-key, not both."
            )
        private_key = f"{prefix}.private.pem"
        public_key = f"{prefix}.public.pem"

    if private_key or public_key:
        if not private_key or not public_key:
            raise ValueError(
                "Authorship proof requires both private and public keys, or --authorship-key-prefix."
            )
        private_path = Path(private_key)
        public_path = Path(public_key)
        if not private_path.exists():
            raise FileNotFoundError(f"Authorship private key not found: {private_key}")
        if not public_path.exists():
            raise FileNotFoundError(f"Authorship public key not found: {public_key}")
        return str(private_path), str(public_path)

    return None, None


def attach_authorship_if_requested(args, payload_path):
    """Attach authorship proof in-place if optional key flags are present."""
    private_key, public_key = resolve_authorship_key_paths(args)
    if not private_key:
        return False

    if not ATTACH_SCRIPT.exists():
        raise FileNotFoundError(f"Authorship attach helper not found: {ATTACH_SCRIPT}")

    payload_path = str(payload_path)
    result = subprocess.run(
        [
            "node",
            str(ATTACH_SCRIPT),
            "--payload",
            payload_path,
            "--private-key",
            private_key,
            "--public-key",
            public_key,
            "--out",
            payload_path,
        ],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, file=sys.stderr)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        raise RuntimeError("Failed to attach authorship proof")

    print("✅ Authorship proof attached to Gateway payload.")
    print("   Boundary: key continuity only; not authority, verification, attestation, reception, or amendment.")
    print("   Keep the private key local. Never submit, paste, upload, or commit it.")
    return True
