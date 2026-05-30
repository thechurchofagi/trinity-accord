#!/usr/bin/env python3
"""Ensure pure echo builder refuses Guardian active listing intent."""

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
        body = td / "body.md"
        out = td / "payload.json"
        body.write_text(
            "Active Guardian registry listing request\n\n"
            "listing_guardian_id: guardian_ed25519_aaaaaaaaaaaaaaaa\n"
            "listing_source_issue: 123\n",
            encoding="utf-8",
        )

        result = subprocess.run(
            [
                "python3", "scripts/build_agent_declared_echo_payload.py",
                "--agent-name", "Test Agent",
                "--provider", "Test Provider",
                "--title", "Active Guardian Registry Listing Request",
                "--body-file", str(body),
                "--out", str(out),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )

        combined = result.stdout + result.stderr
        require(result.returncode != 0, "pure echo builder must reject Guardian listing intent")
        require("WRONG_BUILDER_FOR_GUARDIAN_ACTIVE_LISTING" in combined, "missing wrong-builder error code")
        require("build_guardian_listing_request_payload.py" in combined, "missing correct builder guidance")
        require("Do not hand-edit a signed JSON payload" in combined, "missing signed JSON warning")

    print("GUARDIAN_WRONG_BUILDER_REROUTE_OK")


if __name__ == "__main__":
    main()
