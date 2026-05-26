#!/usr/bin/env python3
"""
Build an authorship challenge for claiming an Echo record.
Generates a challenge object with nonce, timestamps, target hash, and challenge hash.

Usage:
    python3 scripts/build_echo_authorship_challenge.py --target-record path/to/record.json --out challenge.json
    python3 scripts/build_echo_authorship_challenge.py --target-record record.json --expires-hours 48 --out challenge.json
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path


def canonical_json(obj):
    """Produce canonical JSON: sorted keys, no whitespace, UTF-8."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_record(record_path: str) -> str:
    """Hash a record file as-is (raw bytes)."""
    with open(record_path, "rb") as f:
        return sha256_hex(f.read())


def build_challenge(target_hash: str, expires_hours: float) -> dict:
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=expires_hours)

    # Build the challenge object (without challenge_hash first)
    challenge_core = {
        "nonce": os.urandom(32).hex(),
        "created_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "expires_at_utc": expires.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "target_record_hash_sha256": target_hash,
        "canonicalization": "trinityaccord.canonical-json.v1",
    }

    # Compute challenge hash over canonical form
    challenge_hash = sha256_hex(canonical_json(challenge_core))

    challenge = {**challenge_core, "challenge_hash_sha256": challenge_hash}
    return challenge


def main():
    parser = argparse.ArgumentParser(description="Build authorship challenge for Echo record claiming.")
    parser.add_argument("--target-record", required=True, help="Path to the target Echo record JSON file.")
    parser.add_argument("--out", required=True, help="Output path for the challenge JSON.")
    parser.add_argument("--expires-hours", type=float, default=24.0, help="Hours until challenge expires (default: 24).")
    args = parser.parse_args()

    target_path = Path(args.target_record)
    if not target_path.exists():
        print(f"FAIL: Target record not found: {target_path}", file=sys.stderr)
        return 1

    target_hash = hash_record(str(target_path))
    challenge = build_challenge(target_hash, args.expires_hours)

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(challenge, f, indent=2, ensure_ascii=False)

    print(f"Challenge written to {out_path}")
    print(f"  target_hash: {target_hash}")
    print(f"  challenge_hash: {challenge['challenge_hash_sha256']}")
    print(f"  expires: {challenge['expires_at_utc']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
