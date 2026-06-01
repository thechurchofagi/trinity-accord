#!/usr/bin/env python3
"""Build canonical authorship claim message for post-submission claim.

Usage:
    python3 scripts/build_agent_authorship_claim_message.py \
      --issue-number 182 \
      --public-key-sha256 <hash> \
      --payload-sha256 <hash> \
      --out /tmp/claim-message.txt
"""
import argparse
from pathlib import Path


def build_claim_message(issue_number, public_key_sha256, payload_sha256, repo="thechurchofagi/trinity-accord"):
    return "\n".join([
        "TRINITY_AGENT_AUTHORSHIP_CLAIM_V1",
        f"issue_number={issue_number}",
        f"repo={repo}",
        f"authorship_public_key_sha256={public_key_sha256}",
        f"authorship_payload_sha256={payload_sha256}",
        "boundary=key_control_only_not_authority_not_attestation_not_amendment",
    ])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--issue-number", required=True, type=int)
    parser.add_argument("--public-key-sha256", required=True)
    parser.add_argument("--payload-sha256", required=True)
    parser.add_argument("--repo", default="thechurchofagi/trinity-accord")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    msg = build_claim_message(args.issue_number, args.public_key_sha256, args.payload_sha256, args.repo)
    Path(args.out).write_text(msg + "\n", encoding="utf-8")
    print(f"Wrote claim message to {args.out}")
    print(msg)


if __name__ == "__main__":
    main()
