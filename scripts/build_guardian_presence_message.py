#!/usr/bin/env python3
"""Build Guardian presence message for signing.

Usage:
    python3 scripts/build_guardian_presence_message.py --print-message --payload payload.json --public-key key.public.pem --challenge "my-challenge"
    python3 scripts/build_guardian_presence_message.py --print-digest --payload payload.json --public-key key.public.pem --challenge "my-challenge"
    python3 scripts/build_guardian_presence_message.py --print-guardian-id --public-key key.public.pem
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from guardian_common import (
    build_guardian_presence_message,
    guardian_id_from_public_key,
    guardian_payload_sha256,
    sha256_text,
)


def main():
    parser = argparse.ArgumentParser(description="Build Guardian presence message for signing.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--print-message", action="store_true", help="Print the canonical message to sign")
    group.add_argument("--print-digest", action="store_true", help="Print SHA-256 of the canonical message")
    group.add_argument("--print-guardian-id", action="store_true", help="Print the guardian_id derived from public key")

    parser.add_argument("--payload", help="Path to the gateway payload JSON file")
    parser.add_argument("--public-key", required=True, help="Path to Ed25519 public key PEM")
    parser.add_argument("--challenge", default="", help="Challenge string (empty if not provided)")

    args = parser.parse_args()
    public_key_pem = Path(args.public_key).read_text(encoding="utf-8")

    if args.print_guardian_id:
        print(guardian_id_from_public_key(public_key_pem))
        return

    if not args.payload:
        print("ERROR: --payload is required for --print-message and --print-digest", file=sys.stderr)
        sys.exit(1)

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    message = build_guardian_presence_message(payload, public_key_pem, args.challenge)

    if args.print_message:
        print(message)
    elif args.print_digest:
        print(sha256_text(message))


if __name__ == "__main__":
    main()
