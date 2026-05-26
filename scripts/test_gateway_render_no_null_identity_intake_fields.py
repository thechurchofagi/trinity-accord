#!/usr/bin/env python3
"""Test: rendered issue body must not contain null/None for identity intake fields.

Ensures render_gateway_issue_body.py outputs 'not_provided' instead of
null/None for optional identity fields when human is not provided.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_render_without_human() -> None:
    """Render a listing payload without human claimed name; body must use 'not_provided'."""
    # Build a payload first
    payload_path = Path(tempfile.mkdtemp()) / "listing.json"
    subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "build_guardian_listing_request_payload.py"),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--source-issue", "245",
        "--guardian-id", "guardian_ed25519_aaaaaaaaaaaaaaaa",
        "--public-key-sha256", "aaaaaaaaaaaaaaaa" + "0" * 48,
        "--label", "Test Guardian",
        "--out", str(payload_path),
    ], check=True, cwd=str(ROOT))

    # Render the body
    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_gateway_issue_body.py"), str(payload_path)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Renderer failed: {result.stderr}"
    body = result.stdout

    # Must contain the sentinel
    assert "listing_human_claimed_name: not_provided" in body, \
        f"Expected 'listing_human_claimed_name: not_provided' in body"

    # Must NOT contain null/None
    assert "listing_human_claimed_name: None" not in body, \
        "Renderer output 'None' for listing_human_claimed_name"
    assert "listing_human_claimed_name: null" not in body, \
        "Renderer output 'null' for listing_human_claimed_name"

    # Must NOT contain placeholder
    assert "HUMAN_CLAIMED_NAME" not in body, \
        "Renderer output placeholder HUMAN_CLAIMED_NAME"

    # Check guardian identity fields in machine block
    assert "guardian_human_claimed_name: not_provided" in body, \
        f"Expected 'guardian_human_claimed_name: not_provided' in body"
    assert "guardian_human_claimed_name: None" not in body, \
        "Renderer output 'None' for guardian_human_claimed_name"

    print("PASS: test_render_without_human")


def test_render_with_human() -> None:
    """Render a listing payload with human claimed name; body must have the value."""
    payload_path = Path(tempfile.mkdtemp()) / "listing.json"
    subprocess.run([
        sys.executable,
        str(ROOT / "scripts" / "build_guardian_listing_request_payload.py"),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--source-issue", "245",
        "--guardian-id", "guardian_ed25519_bbbbbbbbbbbbbbbb",
        "--public-key-sha256", "bbbbbbbbbbbbbbbb" + "0" * 48,
        "--label", "Dawei Liu",
        "--human-claimed-name", "Dawei Liu",
        "--agent-claimed-id", "TestAgent",
        "--out", str(payload_path),
    ], check=True, cwd=str(ROOT))

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "render_gateway_issue_body.py"), str(payload_path)],
        capture_output=True, text=True, cwd=str(ROOT),
    )
    assert result.returncode == 0, f"Renderer failed: {result.stderr}"
    body = result.stdout

    assert "listing_human_claimed_name: Dawei Liu" in body
    assert "guardian_human_claimed_name: Dawei Liu" in body

    print("PASS: test_render_with_human")


def main() -> None:
    test_render_without_human()
    test_render_with_human()
    print("\nAll renderer null/None identity field tests PASSED.")


if __name__ == "__main__":
    main()
