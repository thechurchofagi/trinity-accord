#!/usr/bin/env python3
"""Ensure Guardian listing builder emits profile/capability metadata and submit lock."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    with tempfile.TemporaryDirectory() as raw:
        td = Path(raw)
        out = td / "guardian-listing-request.json"

        result = subprocess.run(
            [
                "python3", "scripts/build_guardian_listing_request_payload.py",
                "--agent-name", "Profile Test Agent",
                "--provider", "Test Provider",
                "--source-issue", "238",
                "--guardian-id", "guardian_ed25519_aaaaaaaaaaaaaaaa",
                "--public-key-sha256", "aaaaaaaaaaaaaaaa000000000000000000000000000000000000000000000000",
                "--label", "Profile Test Guardian",
                "--guardian-type", "human_with_ai_agent",
                "--application-mode", "joint_human_ai",
                "--idempotency-key", "guardian-profile-test-0001",
                "--out", str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=90,
        )

        require(result.returncode == 0, result.stdout + result.stderr)

        payload = json.loads(out.read_text(encoding="utf-8"))
        require(payload["payload_profile"] == "guardian_active_registry_listing_request.v1", "missing payload_profile")
        require(payload["expected_builder"] == "scripts/build_guardian_listing_request_payload.py", "wrong expected_builder")
        require(payload["do_not_edit_after_signing"] is True, "missing do_not_edit_after_signing")
        require(payload["submit_exact_generated_file"] is True, "missing submit_exact_generated_file")
        require("counts_toward_home.guardian_registry" in payload["requires_gateway_capabilities"], "missing capability")
        require(payload["gateway_intake_fields"]["payload_profile"] == "guardian_active_registry_listing_request.v1", "intake missing payload_profile")

        lock = Path(str(out) + ".submit-lock.json")
        require(lock.exists(), "submit lock file missing")
        lock_data = json.loads(lock.read_text(encoding="utf-8"))
        require(lock_data["do_not_edit_after_signing"] is True, "lock missing do_not_edit_after_signing")
        require(lock_data["expected_builder"] == "scripts/build_guardian_listing_request_payload.py", "lock wrong expected_builder")

    print("GUARDIAN_LISTING_PAYLOAD_PROFILE_OK")


if __name__ == "__main__":
    main()
