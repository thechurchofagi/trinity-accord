#!/usr/bin/env python3
"""Contract: archive / OTS workflows rebuild status before homepage."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require_sequence(path: str, required_adds: list[str] | None = None) -> None:
    text = (ROOT / path).read_text(encoding="utf-8")
    status = "generate_record_chain_status.py"
    home = "generate_public_home_status.py"
    patch = "patch_public_home_status_primary.py"
    for marker in (status, home, patch, "api/record-chain-status.json", "api/public-home-status.json", "index.md"):
        if marker not in text:
            fail(f"{path} missing {marker}")
    if not (text.index(status) < text.index(home) < text.index(patch)):
        fail(f"{path} must regenerate record-chain-status before public-home before patcher")
    for marker in required_adds or []:
        if marker not in text:
            fail(f"{path} missing commit/add marker {marker}")


for workflow in [
    ".github/workflows/record-chain-anchor.yml",
    ".github/workflows/record-chain-head-ots-anchor.yml",
    ".github/workflows/record-chain-ots-upgrade.yml",
    ".github/workflows/native-ots-upgrade-watch.yml",
    ".github/workflows/record-chain-arweave-archive.yml",
    ".github/workflows/record-chain-append.yml",
]:
    require_sequence(workflow)

print("PASS: homepage-refresh workflows rebuild chain status before homepage")
