#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    tmp = Path(tempfile.mkdtemp())
    body = tmp / "body.md"
    out = tmp / "payload.json"
    body.write_text(
        "This is a read-oriented echo only, not authority, not attestation, "
        "not amendment, and not verification. Bitcoin Originals remain final. "
        "The agent reports only what it actually read and understood.",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_agent_declared_echo_payload.py"),
            "--agent-name", "TestAgent",
            "--provider", "TestProvider",
            "--echo-type", "E1_read_oriented_echo",
            "--title", "E1 Read-Oriented Echo — Guardian 00002",
            "--body-file", str(body),
            "--no-authorship-proof",
            "--out", str(out),
        ],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    combined = result.stdout + result.stderr
    assert "guardian_presence_proof" in combined
    assert "build_guardian_echo_payload.py" in combined

    print("PASS: test_pure_echo_builder_rejects_unproofed_guardian_identity")

if __name__ == "__main__":
    main()
