#!/usr/bin/env python3
"""Test that build_agent_declared_archive_payload.py emits correct agent_readback_sha256 for all V0-V5 levels."""

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_agent_declared_archive_payload.py"


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


LEVELS = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5"]


def test_level(level: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        out = f.name

    cmd = [
        sys.executable, str(SCRIPT),
        "--agent-name", f"TestAgent-{level}",
        "--provider", "TestProvider",
        "--declared-level", level,
        "--reception-initiation-class", "externally_requested",
        "--reception-initiation-basis", "explicit_verification_request",
        "--first-entry-url", "https://www.trinityaccord.org/",
        "--first-entry-type", "homepage",
        "--what-checked", "Read the Trinity Accord homepage and understood the authority boundary.",
        "--limitation", "This is a reading echo only, not authority, not attestation, and not amendment.",
        "--no-authorship-proof",
        "--out", out,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if result.returncode != 0:
        raise RuntimeError(f"Builder failed for {level}: {result.stderr}")

    payload = json.loads(Path(out).read_text(encoding="utf-8"))
    oath = payload.get("agent_integrity_declaration", {}).get("verification_oath", {})

    readback = oath.get("agent_readback", "")
    if not readback:
        raise AssertionError(f"{level}: agent_readback is empty")

    expected_sha = sha256_text(readback.strip())
    actual_sha = oath.get("agent_readback_sha256")

    if not actual_sha:
        raise AssertionError(f"{level}: agent_readback_sha256 is missing")

    if actual_sha != expected_sha:
        raise AssertionError(
            f"{level}: agent_readback_sha256 mismatch. "
            f"expected={expected_sha}, actual={actual_sha}"
        )

    Path(out).unlink(missing_ok=True)


def main():
    passed = 0
    failed = 0
    for level in LEVELS:
        try:
            test_level(level)
            print(f"  PASS: {level}")
            passed += 1
        except Exception as e:
            print(f"  FAIL: {level}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
