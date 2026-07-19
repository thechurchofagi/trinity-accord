#!/usr/bin/env python3
"""Bind every Node-based workflow to the repository's exact .node-version."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"
TARGETS = (
    "backup-nft-arweave-mirror.yml",
    "backup-nft-cars.yml",
    "backup-nft-individual-v2.yml",
    "backup-nft-individual.yml",
    "nft-identity-index-integrity.yml",
    "pre-scale-e2e-orchestrator-v2.yml",
    "summarize-evidence-chain.yml",
    "verify-bitcoin-tx-anchor.yml",
    "verify-btc-signature-coverage.yml",
    "verify-dag-and-signed-cids.yml",
    "verify-dag-digest.yml",
    "verify-eth-witness.yml",
    "verify-full-evidence-chain.yml",
    "verify-onchain-tokenuri.yml",
    "verify-ots-time-anchor.yml",
    "verify-release-assets.yml",
    "verify-v3plus-signed-release.yml",
)
PATTERN = re.compile(
    r"(?m)^(?P<indent>\s*)node-version:\s*[\"']?\d+(?:\.\d+){0,2}[\"']?\s*$"
)

for name in TARGETS:
    path = WORKFLOWS / name
    text = path.read_text(encoding="utf-8")
    updated, count = PATTERN.subn(
        lambda match: f'{match.group("indent")}node-version-file: ".node-version"',
        text,
    )
    if count < 1:
        raise SystemExit(f"{name}: no hard-coded Node version found")
    path.write_text(updated, encoding="utf-8")
    print(f"{name}: replaced {count} hard-coded Node version declaration(s)")

print("ROUND6_NODE_RUNTIME_ALIGNMENT_APPLIED")
