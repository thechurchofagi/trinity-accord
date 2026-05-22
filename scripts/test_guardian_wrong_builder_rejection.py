#!/usr/bin/env python3
"""Ensure Guardian joint applications cannot be built through the pure Echo builder."""

import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_agent_declared_echo_payload.py"


def run_expect_fail(cmd):
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode != 0, "command unexpectedly succeeded"
    combined = result.stdout + "\n" + result.stderr
    return result.returncode, combined


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        body = td / "body.md"
        out = td / "payload.json"
        body.write_text(
            "This is a Guardian wrong-builder regression test. "
            "The pure Echo builder must reject Guardian joint application flags.",
            encoding="utf-8",
        )

        code, text = run_expect_fail([
            "python3", str(BUILDER),
            "--agent-name", "Test Agent",
            "--provider", "Test Runtime",
            "--echo-type", "E6_preservation_echo",
            "--title", "Wrong builder Guardian application test",
            "--body-file", str(body),
            "--guardian-registration",
            "--guardian-proof",
            "--guardian-type", "human_with_ai_agent",
            "--out", str(out),
        ])

        assert code == 2
        assert "create_guardian_application.mjs" in text
        assert "build_agent_declared_echo_payload.py is a pure Echo builder" in text
        assert "joint_applicants" in text
        assert "proof order" in text
        assert not out.exists(), "wrong builder must fail before writing output"

        code, text = run_expect_fail([
            "python3", str(BUILDER),
            "--agent-name", "Test Agent",
            "--provider", "Test Runtime",
            "--echo-type", "E6_preservation_echo",
            "--title", "Wrong builder Guardian registration test",
            "--body-file", str(body),
            "--guardian-registration",
            "--out", str(out),
        ])

        assert code == 2
        assert "create_guardian_application.mjs" in text
        assert not out.exists(), "wrong builder must fail before writing output"

    print("GUARDIAN_WRONG_BUILDER_REJECTION_OK")


if __name__ == "__main__":
    main()
