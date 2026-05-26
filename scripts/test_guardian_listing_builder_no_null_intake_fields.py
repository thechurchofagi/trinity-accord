#!/usr/bin/env python3
"""Test: guardian listing builder must not emit null in gateway_intake_fields.

Regression test for optional identity fields producing JSON null
instead of "not_provided" sentinel string.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build_payload(extra_args: list[str] | None = None) -> dict:
    out = Path(tempfile.mkdtemp()) / "listing.json"
    cmd = [
        sys.executable,
        str(ROOT / "scripts" / "build_guardian_listing_request_payload.py"),
        "--agent-name", "TestAgent",
        "--provider", "TestProvider",
        "--source-issue", "245",
        "--guardian-id", "guardian_ed25519_aaaaaaaaaaaaaaaa",
        "--public-key-sha256", "aaaaaaaaaaaaaaaa" + "0" * 48,
        "--label", "Test Guardian",
        "--out", str(out),
    ]
    if extra_args:
        cmd.extend(extra_args)
    subprocess.run(cmd, check=True, cwd=str(ROOT))
    return json.loads(out.read_text(encoding="utf-8"))


def test_no_human_claimed_name() -> None:
    """Without --human-claimed-name, intake fields must be 'not_provided', not null."""
    payload = build_payload()
    fields = payload["gateway_intake_fields"]
    claims = payload["guardian_listing_request"]["identity_claims"]

    # identity_claims.human = null is correct
    assert claims["human"] is None, "identity_claims.human should be None when not provided"

    # But gateway_intake_fields must NOT have null
    assert fields["listing_human_claimed_name"] == "not_provided"
    assert fields["listing_human_claimed_name_sha256"] == "not_provided"
    # agent_claimed_id defaults to agent_name when not explicitly provided
    assert fields["listing_agent_claimed_id"] == "TestAgent"
    assert fields["listing_agent_claimed_id_sha256"] is not None

    # No null values anywhere in gateway_intake_fields
    null_keys = [k for k, v in fields.items() if v is None]
    assert not null_keys, f"gateway_intake_fields has null values: {null_keys}"

    print("PASS: test_no_human_claimed_name")


def test_with_human_claimed_name() -> None:
    """With --human-claimed-name, intake fields should have the actual value."""
    payload = build_payload([
        "--human-claimed-name", "Dawei Liu",
        "--agent-claimed-id", "TestAgent",
    ])
    fields = payload["gateway_intake_fields"]
    claims = payload["guardian_listing_request"]["identity_claims"]

    assert claims["human"]["claimed_name"] == "Dawei Liu"
    assert fields["listing_human_claimed_name"] == "Dawei Liu"
    assert fields["listing_human_claimed_name_sha256"] == claims["human"]["claimed_name_sha256"]
    assert fields["listing_agent_claimed_id"] == "TestAgent"

    # No null values
    null_keys = [k for k, v in fields.items() if v is None]
    assert not null_keys, f"gateway_intake_fields has null values: {null_keys}"

    print("PASS: test_with_human_claimed_name")


def main() -> None:
    test_no_human_claimed_name()
    test_with_human_claimed_name()
    print("\nAll gateway_intake_fields null regression tests PASSED.")


if __name__ == "__main__":
    main()
