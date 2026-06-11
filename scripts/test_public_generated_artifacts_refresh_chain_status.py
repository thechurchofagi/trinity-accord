#!/usr/bin/env python3
"""Contract: public artifact refresh must rebuild record-chain status first."""
from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "update_public_generated_artifacts.py"


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


text = SCRIPT.read_text(encoding="utf-8")
required = [
    "scripts/generate_record_chain_status.py",
    "scripts/generate_public_home_status.py",
    "scripts/patch_public_home_status_primary.py",
    "scripts/generate_sitemap.py",
]
for item in required:
    if item not in text:
        fail(f"missing refresh step: {item}")

positions = [text.index(item) for item in required]
if positions != sorted(positions):
    fail("refresh steps must run record-chain-status -> public-home -> patcher -> sitemap")

print("PASS: public generated artifact refresh rebuilds chain status before homepage")
