#!/usr/bin/env python3
"""Print exact Builder manifest diagnostics, then run the full sync contract."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import check_builder_receipt_boundary_sync_core as core

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
MANIFEST = ROOT / "api" / "record-chain-builder-bundles.v1.json"


def main() -> int:
    builder_bytes = BUILDER.read_bytes()
    declared = json.loads(MANIFEST.read_text(encoding="utf-8")).get("canonical_builder", {})
    print(
        "BUILDER_MANIFEST_DIAGNOSTIC "
        f"actual_sha256={hashlib.sha256(builder_bytes).hexdigest()} "
        f"actual_size_bytes={len(builder_bytes)} "
        f"declared_sha256={declared.get('sha256')} "
        f"declared_size_bytes={declared.get('size_bytes')}"
    )
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
