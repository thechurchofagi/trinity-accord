#!/usr/bin/env python3
"""Test that download_and_run_builder_bundle.py covers all routes and is safe."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    helper = ROOT / "scripts" / "download_and_run_builder_bundle.py"
    if not helper.exists():
        print("FAIL: download_and_run_builder_bundle.py does not exist")
        return 1

    text = helper.read_text(encoding="utf-8")
    errors = []

    # All routes must be present
    required = [
        "pure_echo",
        "v0_v5_agent_declared_archive",
        "guardian_application_stage_1",
        "guardian_listing_stage_2",
        "guardian_signed_echo",
        "verify_sha256",
        "extract_bundle",
        "/gateway/preflight",
        "/agent-submit",
    ]
    for r in required:
        if r not in text:
            errors.append(f"missing required string: {r}")

    # Forbidden
    forbidden = ["/gateway/submit"]
    for f in forbidden:
        if f in text:
            errors.append(f"forbidden string present: {f}")

    # Guardian Stage 1 must use node for .mjs
    if '"node", str(extract_dir / entrypoint)' not in text and "'node', str(extract_dir / entrypoint)" not in text:
        errors.append("Guardian Stage 1 must use node to run .mjs builder")

    # Guardian Stage 1 must pass --out
    if '"--out", args.out' not in text and "'--out', args.out" not in text:
        errors.append("Guardian Stage 1 must pass --out args.out")

    # Must protect against unsafe tar paths
    if "resolved_target" not in text or "Refusing unsafe tar path" not in text:
        errors.append("helper must protect against unsafe tar paths")

    # Must fail closed when API sha256 is empty
    if "has no sha256 recorded" not in text:
        errors.append("helper must fail closed when API sha256 is empty")

    # Must use --readback (not --readback-file) for v0_v5 and guardian stage 1
    if '"--readback", readback' not in text and "'--readback', readback" not in text:
        errors.append("helper must pass --readback with file content for v0_v5 and guardian stage 1")

    # Must have route-specific readback targets
    if "READBACK_TARGETS" not in text:
        errors.append("helper must have route-specific READBACK_TARGETS")

    # Must validate required args before download
    if "require_args" not in text:
        errors.append("helper must validate required args before download")

    if errors:
        print("FAIL: test_download_helper_covers_all_routes:")
        for e in errors:
            print("  -", e)
        return 1

    print("PASS: test_download_helper_covers_all_routes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
