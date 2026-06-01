#!/usr/bin/env python3
"""Build SHA-256 manifest for legacy/gateway-v1/ archive."""
from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEGACY_DIR = ROOT / "legacy" / "gateway-v1"
MANIFEST_PATH = LEGACY_DIR / "MANIFEST.sha256.json"


def main() -> int:
    if not LEGACY_DIR.exists():
        print("FAIL: legacy/gateway-v1/ does not exist")
        return 1

    files = []
    for p in sorted(LEGACY_DIR.rglob("*")):
        if not p.is_file():
            continue
        if p.name == "MANIFEST.sha256.json":
            continue
        rel = str(p.relative_to(ROOT))
        sha = hashlib.sha256(p.read_bytes()).hexdigest()
        files.append({"path": rel, "sha256": sha})

    manifest = {
        "schema": "trinityaccord.legacy-gateway-v1-manifest.v1",
        "status": "historical_archive_only",
        "not_primary_path": True,
        "not_active_runtime": True,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "hash_algorithm": "sha256",
        "files": files,
        "boundary": {
            "not_authority": True,
            "not_governance": True,
            "not_attestation": True,
            "not_successor_reception": True,
            "not_amendment": True,
            "bitcoin_originals_prevail": True,
        },
    }

    MANIFEST_PATH.write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {MANIFEST_PATH.relative_to(ROOT)} with {len(files)} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
