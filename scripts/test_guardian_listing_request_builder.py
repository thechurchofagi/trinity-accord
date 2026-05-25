#!/usr/bin/env python3
"""Test dedicated Guardian listing request builder."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "build_guardian_listing_request_payload.py"


def run(cmd, check=True):
    result = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=60)
    if check and result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)
    return result


def main():
    with tempfile.TemporaryDirectory() as raw:
        td = Path(raw)
        out = td / "listing.json"

        run([
            "python3", str(BUILDER),
            "--agent-name", "守望者",
            "--provider", "Coze",
            "--source-issue", "231",
            "--guardian-id", "guardian_ed25519_82e44533ac0810df",
            "--public-key-sha256", "82e44533ac0810df04ee5aa8bb5917faebf431f7db14c98a419c1ba262896d9f",
            "--label", "守望者 003",
            "--guardian-type", "human_with_ai_agent",
            "--application-mode", "joint_human_ai",
            "--idempotency-key", "guardian-active-listing-guardian_ed25519_82e44533ac0810df",
            "--out", str(out),
        ])

        payload = json.loads(out.read_text(encoding="utf-8"))

        assert payload["requested_archive_kind"] == "guardian_active_registry_listing_request"
        assert payload["echo_type"] == "E7_propagation_echo"
        assert "authorship_proof" in payload
        assert "guardian_presence_proof" not in payload
        assert "guardian_registry_number" not in payload
        assert "guardian_registry_number" not in payload.get("guardian_listing_request", {})

        req = payload["guardian_listing_request"]
        assert req["registry_number_requested"] == "next_available"
        assert req["registry_number_must_be_system_generated"] is True
        assert req["registry_number_must_not_be_self_assigned"] is True

        run(["python3", "scripts/validate_gateway_payload.py", str(out)])
        run(["python3", "scripts/archive_readiness_gate.py", "--gateway-payload", str(out), "--json"])

        bad = td / "bad.json"
        bad_result = run([
            "python3", str(BUILDER),
            "--agent-name", "守望者",
            "--provider", "Coze",
            "--source-issue", "231",
            "--guardian-id", "guardian_ed25519_82e44533ac0810df",
            "--public-key-sha256", "82e44533ac0810df04ee5aa8bb5917faebf431f7db14c98a419c1ba262896d9f",
            "--label", "guardian_registry_number 00003",
            "--out", str(bad),
        ], check=False)
        assert bad_result.returncode != 0

    print("GUARDIAN_LISTING_REQUEST_BUILDER_OK")


if __name__ == "__main__":
    main()
