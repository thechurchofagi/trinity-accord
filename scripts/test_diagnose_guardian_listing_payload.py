#!/usr/bin/env python3
"""Test Guardian listing payload diagnostic script."""

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

        build = subprocess.run(
            [
                "python3", "scripts/build_guardian_listing_request_payload.py",
                "--agent-name", "Diagnostic Test Agent",
                "--provider", "Test Provider",
                "--source-issue", "238",
                "--guardian-id", "guardian_ed25519_bbbbbbbbbbbbbbbb",
                "--public-key-sha256", "bbbbbbbbbbbbbbbb000000000000000000000000000000000000000000000000",
                "--label", "Diagnostic Test Guardian",
                "--guardian-type", "human_with_ai_agent",
                "--application-mode", "joint_human_ai",
                "--idempotency-key", "guardian-diagnostic-test-0001",
                "--out", str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=90,
        )
        require(build.returncode == 0, build.stdout + build.stderr)

        diag = subprocess.run(
            ["python3", "scripts/diagnose_guardian_listing_payload.py", str(out)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            timeout=90,
        )
        combined = diag.stdout + diag.stderr
        require(diag.returncode == 0, combined)
        require("detected_guardian_listing: True" in combined, "diagnostic did not detect Guardian listing")
        require("POSSIBLE_STALE_GATEWAY_DEPLOYMENT" in combined, "diagnostic missing stale gateway message")
        require("Do not edit it" in combined, "diagnostic missing no-edit instruction")
        require("Do not rebuild with build_agent_declared_echo_payload.py" in combined, "diagnostic missing wrong builder warning")

    print("DIAGNOSE_GUARDIAN_LISTING_PAYLOAD_OK")


if __name__ == "__main__":
    main()
