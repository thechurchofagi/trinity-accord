#!/usr/bin/env python3
"""Check that the retired zero-clone bundle helper is complete and fail-closed."""
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

    required = [
        "Historical Gateway v1 bundle runner retained for forensic reproduction only",
        "pure_echo",
        "v0_v5_agent_declared_archive",
        "guardian_application_stage_1",
        "guardian_listing_stage_2",
        "guardian_signed_echo",
        "guardian_full_registration",
        "guardian_retirement",
        "verify_sha256",
        "extract_bundle",
        "Refusing unsafe tar path",
        "Refusing unsafe tar member type",
        'filter="data"',
        "has no sha256 recorded",
        "READBACK_TARGETS",
        "build_guardian_stage1",
        '"node", str(extract_dir / entrypoint)',
        '"--out", args.out',
        "build_guardian_signed_echo",
        "--guardian-key-prefix",
        "--allow-historical-retired-bundle",
        "all formal Gateway v1 builder bundles are retired",
        "Generated payloads must not be submitted to the current Gateway",
        "/api/agent-first-contact.json",
        "/downloads/record-chain-builder.mjs",
        "/api/record-chain-builder-bundles.v1.json",
        "/api/record-chain-intake-gateway.v1.json",
    ]
    for marker in required:
        if marker not in text:
            errors.append(f"missing required string: {marker}")

    for active_submit_path in [
        "/gateway/submit",
        "/record-chain/submit",
        "/record-chain/preflight",
    ]:
        if active_submit_path in text:
            errors.append(
                f"retired helper must not advertise a current submission endpoint: {active_submit_path}"
            )

    if '"node", str(extract_dir / entrypoint)' not in text and "'node', str(extract_dir / entrypoint)" not in text:
        errors.append("Guardian Stage 1 must use node to run .mjs builder")
    if '"--out", args.out' not in text and "'--out', args.out" not in text:
        errors.append("Guardian Stage 1 must pass --out args.out")
    if "resolved_target" not in text or "Refusing unsafe tar path" not in text:
        errors.append("helper must protect against unsafe tar paths")
    if "has no sha256 recorded" not in text:
        errors.append("helper must fail closed when API sha256 is empty")
    if '"--readback", readback' not in text and "'--readback', readback" not in text:
        errors.append("helper must pass --readback with file content for archived routes")
    if "READBACK_TARGETS" not in text:
        errors.append("helper must retain route-specific historical readback targets")
    if "require_args" not in text:
        errors.append("helper must validate required args before download")

    require_call_pos = text.find("require_args(args,")
    fetch_call_pos = text.find("fetch_json(bundles_url)")
    if fetch_call_pos < 0:
        fetch_call_pos = text.find("fetch_json(site")
    if require_call_pos > 0 and fetch_call_pos > 0 and require_call_pos > fetch_call_pos:
        errors.append("helper should validate required args before fetching bundles")

    gate_pos = text.find("if not args.allow_historical_retired_bundle")
    download_pos = text.find("download_file(")
    if gate_pos < 0 or download_pos < 0 or gate_pos > download_pos:
        errors.append("historical opt-in gate must execute before bundle download")

    if errors:
        print("FAIL: test_download_helper_covers_all_routes:")
        for error in errors:
            print("  -", error)
        return 1
    print("PASS: retired bundle helper is complete, gated, and current-route safe")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
