#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRYPOINT = ROOT / "downloads" / "record-chain-builder.mjs"
RECOVERY = ROOT / "downloads" / "record-chain-builder-recovery.mjs"
CORE = ROOT / "downloads" / "record-chain-builder-core.mjs"
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
    "ambiguous_submit_readonly_recovery",
    "ed25519_authorship_proof",
    "self_reported_provenance",
]


def _digest(path: Path) -> tuple[str, int]:
    payload = path.read_bytes()
    return hashlib.sha256(payload).hexdigest(), len(payload)


def main() -> int:
    for path in (ENTRYPOINT, RECOVERY, CORE, MANIFEST):
        if not path.exists():
            raise SystemExit(f"missing builder artifact: {path}")

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entry_sha256, entry_size = _digest(ENTRYPOINT)
    recovery_sha256, recovery_size = _digest(RECOVERY)
    core_sha256, core_size = _digest(CORE)

    canonical = data.setdefault("canonical_builder", {})
    canonical["sha256"] = entry_sha256
    canonical["size_bytes"] = entry_size
    canonical["architecture"] = "contract_entrypoint_recovery_wrapper_core_v1"

    recovery = canonical.setdefault("recovery_wrapper", {})
    recovery.update(
        {
            "url": "/downloads/record-chain-builder-recovery.mjs",
            "sha256": recovery_sha256,
            "size_bytes": recovery_size,
            "read_only_recovery": True,
            "maximum_submit_posts": 1,
            "must_match_sha256_and_size_before_distribution": True,
        }
    )

    core = canonical.setdefault("core", {})
    core.update(
        {
            "url": "/downloads/record-chain-builder-core.mjs",
            "sha256": core_sha256,
            "size_bytes": core_size,
            "repository_local_companion": True,
            "automatically_fetched_when_companion_missing": True,
            "must_match_sha256_and_size_before_execution": True,
        }
    )

    supports = list(canonical.get("supports") or [])
    for value in REQUIRED_SUPPORTS:
        if value not in supports:
            supports.append(value)
    canonical["supports"] = supports

    MANIFEST.write_text(
        json.dumps(data, indent=2, ensure_ascii=False, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(f"updated {MANIFEST.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
