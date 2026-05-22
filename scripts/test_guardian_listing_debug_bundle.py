#!/usr/bin/env python3
"""Test: Guardian listing debug bundle."""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False, mode="w") as f:
        out_path = f.name

    rc, out = subprocess.run(
        ["python3", "scripts/build_guardian_listing_request_payload.py",
         "--agent-name", "Bundle Test", "--provider", "Test",
         "--source-issue", "9996", "--guardian-id", "guardian_ed25519_dddddddddddddddd",
         "--public-key-sha256", "dddddddddddddddd000000000000000000000000000000000000000000000000",
         "--label", "Bundle Guardian", "--guardian-type", "human_with_ai_agent",
         "--application-mode", "joint_human_ai", "--idempotency-key", "bundle-test",
         "--out", out_path],
        cwd=str(ROOT), text=True, capture_output=True, timeout=120
    ).returncode
    if rc != 0:
        print("FAIL: build payload")
        return 1

    result = subprocess.run(
        ["python3", "scripts/build_guardian_listing_debug_bundle.py", out_path],
        cwd=str(ROOT), text=True, capture_output=True, timeout=60
    )
    print(result.stdout)
    if result.returncode != 0:
        print("FAIL: debug bundle script")
        return 1

    bundle_path = Path(out_path + ".debug-bundle.json")
    if not bundle_path.exists():
        print("FAIL: debug bundle file not created")
        return 1

    bundle = json.loads(bundle_path.read_text())
    required_keys = [
        "fingerprint",
        "authorship_canonical_contract",
        "canonical_payload_without_authorship",
        "build_agent_authorship_message_print_digest",
        "build_agent_authorship_message_print_message",
        "validate_gateway_payload",
        "archive_readiness_gate",
    ]
    missing = [k for k in required_keys if k not in bundle]
    if missing:
        print(f"FAIL: missing keys: {missing}")
        return 1

    print("PASS: debug bundle contains all required keys")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
