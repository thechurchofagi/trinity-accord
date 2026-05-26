#!/usr/bin/env python3
"""Static guard: builders that write agent_readback must also write/readback-normalize sha."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

BUILDER_FILES = [
    "scripts/build_agent_declared_archive_payload.py",
    "scripts/build_agent_declared_echo_payload.py",
    "scripts/build_guardian_listing_request_payload.py",
    "scripts/create_guardian_application.mjs",
]


def main() -> None:
    missing = []

    for rel in BUILDER_FILES:
        path = ROOT / rel
        text = path.read_text(encoding="utf-8")

        has_readback = "agent_readback" in text
        has_sha = "agent_readback_sha256" in text
        has_normalizer = (
            "normalize_oath_readback_integrity" in text
            or "normalizeOathReadbackIntegrity" in text
            or "build_verification_oath_v2" in text
            or "build_guardian_listing_oath_v1" in text
        )

        if has_readback and not (has_sha or has_normalizer):
            missing.append(rel)

    if missing:
        raise SystemExit(
            "Builders with agent_readback but no readback sha / normalizer: "
            + ", ".join(missing)
        )

    print("PASS: test_all_verification_oath_builders_have_readback_sha")


if __name__ == "__main__":
    main()
