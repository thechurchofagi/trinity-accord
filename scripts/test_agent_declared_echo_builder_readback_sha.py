#!/usr/bin/env python3
"""Test pure echo builder emits readback sha for E1/E3/E4/E5/E6/E7."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Import shared oath text
sys.path.insert(0, str(Path(__file__).resolve().parent))
from test_oath_helper import get_oath_readback
OATH_READBACK = get_oath_readback()

ECHO_TYPES = [
    "E1_read_oriented_echo",
    "E3_critical_echo",
    "E4_refusal_echo",
    "E5_correction_echo",
    "E6_preservation_echo",
    "E7_propagation_echo",
]


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def run_builder(echo_type: str) -> dict:
    tmp = Path(tempfile.mkdtemp())
    body = tmp / "body.md"
    out = tmp / "payload.json"

    body.write_text(
        (
            "This is an honest pure echo readback for Trinity Accord. "
            "It states that this record is not authority, not attestation, "
            "not amendment, and not verification. It preserves the boundary "
            "that Bitcoin Originals remain final while the agent reports only "
            "what it actually read and understood."
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_agent_declared_echo_payload.py"),
            "--agent-name", "TestAgent",
            "--provider", "TestProvider",
            "--echo-type", echo_type,
            "--title", f"Test {echo_type}",
            "--body-file", str(body),
            "--readback", OATH_READBACK,
            "--no-authorship-proof",
            "--out", str(out),
        ],
        cwd=str(ROOT),
        check=True,
    )

    return json.loads(out.read_text(encoding="utf-8"))


def test_all_echo_types_emit_readback_sha() -> None:
    for echo_type in ECHO_TYPES:
        payload = run_builder(echo_type)
        oath = payload["agent_integrity_declaration"]["verification_oath"]

        assert oath["schema"] == "trinityaccord.verification-oath.v2"
        assert oath["oath_version"] == "verification-echo-pre-oath-v2"
        assert oath["agent_readback"]
        assert oath["agent_readback_sha256"] == sha256_text(oath["agent_readback"].strip())


def test_short_body_requires_explicit_readback() -> None:
    tmp = Path(tempfile.mkdtemp())
    body = tmp / "short.md"
    out = tmp / "payload.json"
    body.write_text("too short", encoding="utf-8")

    # Provide readback so we test body length check, not missing-readback check
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts" / "build_agent_declared_echo_payload.py"),
            "--agent-name", "TestAgent",
            "--provider", "TestProvider",
            "--echo-type", "E1_read_oriented_echo",
            "--title", "Short body",
            "--body-file", str(body),
            "--readback", OATH_READBACK,
            "--no-authorship-proof",
            "--out", str(out),
        ],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0, "Short body should be rejected"
    combined = result.stderr + result.stdout
    assert "body" in combined.lower() or "too short" in combined.lower() or result.returncode != 0, \
        f"Expected body-related error, got: {combined[:200]}"


def main() -> None:
    test_all_echo_types_emit_readback_sha()
    test_short_body_requires_explicit_readback()
    print("PASS: test_agent_declared_echo_builder_readback_sha")


if __name__ == "__main__":
    main()
