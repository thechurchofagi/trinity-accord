#!/usr/bin/env python3
"""Build canonical authorship message from a Gateway payload.

Usage:
    python3 scripts/build_agent_authorship_message.py payload.json --print-message
    python3 scripts/build_agent_authorship_message.py payload.json --print-digest
    python3 scripts/build_agent_authorship_message.py payload.json --message-out /tmp/msg.txt --digest-out /tmp/digest.txt
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from agent_authorship_common import (
    authorship_canonical_contract,
    authorship_payload_sha256,
    build_authorship_message,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("payload", help="Path to payload JSON")
    parser.add_argument("--print-message", action="store_true")
    parser.add_argument("--print-digest", action="store_true")
    parser.add_argument("--print-contract", action="store_true")
    parser.add_argument("--message-out")
    parser.add_argument("--digest-out")
    args = parser.parse_args()

    payload = json.loads(Path(args.payload).read_text(encoding="utf-8"))
    message = build_authorship_message(payload)
    digest = authorship_payload_sha256(payload)

    if args.print_message:
        print(message, end="")
    if args.print_digest:
        print(digest)
    if args.print_contract:
        print(json.dumps(authorship_canonical_contract(), indent=2, ensure_ascii=False))
    if args.message_out:
        Path(args.message_out).write_text(message, encoding="utf-8")
    if args.digest_out:
        Path(args.digest_out).write_text(digest + "\n", encoding="utf-8")

    if not any([args.print_message, args.print_digest, args.print_contract, args.message_out, args.digest_out]):
        print(message)
        print(f"\npayload_sha256: {digest}")


if __name__ == "__main__":
    main()
