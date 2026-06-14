#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
MANIFEST = ROOT / "api" / "record-chain-builder-bundles.v1.json"

REQUIRED_SUPPORTS = [
    "echo",
    "verification",
    "guardian_application",
    "guardian_retirement",
    "propagation",
    "correction",
    "classification_update",
    "context_insufficient_notice",
    "preflight",
    "submit",
    "ed25519_authorship_proof",
]


def main() -> int:
    if not BUILDER.exists():
        raise SystemExit(f"missing builder: {BUILDER}")
    if not MANIFEST.exists():
        raise SystemExit(f"missing manifest: {MANIFEST}")

    builder_bytes = BUILDER.read_bytes()
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))

    canonical = data.setdefault("canonical_builder", {})
    canonical["sha256"] = hashlib.sha256(builder_bytes).hexdigest()
    canonical["size_bytes"] = len(builder_bytes)

    supports = list(canonical.get("supports") or [])
    for value in REQUIRED_SUPPORTS:
        if value not in supports:
            supports.append(value)
    canonical["supports"] = supports

    MANIFEST.write_text(
        json.dumps(data, indent=2, sort_keys=False, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"updated {MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
