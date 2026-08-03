#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"
BUILDER_CORE = ROOT / "downloads" / "record-chain-builder-core.mjs"
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
    for path in (BUILDER, BUILDER_CORE, MANIFEST):
        if not path.exists():
            raise SystemExit(f"missing builder artifact: {path}")

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    wrapper_sha256, wrapper_size = _digest(BUILDER)
    core_sha256, core_size = _digest(BUILDER_CORE)

    canonical = data.setdefault("canonical_builder", {})
    canonical["sha256"] = wrapper_sha256
    canonical["size_bytes"] = wrapper_size
    canonical["architecture"] = "verified_bootstrap_wrapper_v1"

    core = canonical.setdefault("core", {})
    core["url"] = "/downloads/record-chain-builder-core.mjs"
    core["sha256"] = core_sha256
    core["size_bytes"] = core_size
    core["repository_local_companion"] = True
    core["automatically_fetched_when_companion_missing"] = True
    core["must_match_sha256_and_size_before_execution"] = True

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
