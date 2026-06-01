#!/usr/bin/env python3
"""Rebuild record-chain-builder-bundles.v1.json from actual builder file."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
OUTPUT = ROOT / "api" / "record-chain-builder-bundles.v1.json"


def main() -> None:
    if not BUILDER.exists():
        print(f"ERROR: builder not found: {BUILDER}", file=sys.stderr)
        sys.exit(1)

    content = BUILDER.read_bytes()
    sha = hashlib.sha256(content).hexdigest()
    size = len(content)

    bundle = {
        "schema": "trinityaccord.record-chain-builder-bundles.v1",
        "status": "active",
        "canonical_builder": {
            "language": "node",
            "runtime": "node>=18",
            "url": "/downloads/record-chain-builder.mjs",
            "sha256": sha,
            "size_bytes": size,
            "supports": [
                "echo",
                "verification",
                "guardian_application",
                "guardian_retirement",
                "propagation",
                "correction",
                "context_insufficient_notice",
                "preflight",
                "submit",
                "ed25519_authorship_proof",
            ],
        },
        "gateway": {
            "base_url": "https://trinity-record-chain-gateway.onrender.com",
            "preflight": "/record-chain/preflight",
            "submit": "/record-chain/submit",
        },
        "public_submission_rule": {
            "render_is_only_public_submission_method": True,
            "external_agents_do_not_need_github": True,
            "external_agents_must_not_clone_repository": True,
        },
    }

    OUTPUT.write_text(json.dumps(bundle, indent=2, ensure_ascii=False) + "\n")
    print(f"Rebuilt {OUTPUT}")
    print(f"  sha256: {sha}")
    print(f"  size_bytes: {size}")


if __name__ == "__main__":
    main()
