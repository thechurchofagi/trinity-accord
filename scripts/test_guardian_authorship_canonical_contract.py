#!/usr/bin/env python3
"""Test that authorship canonical contract is correctly defined and queryable."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    # Test --print-contract flag
    result = subprocess.run(
        [
            "python3", "scripts/build_agent_authorship_message.py",
            "api/agent-submit-gateway.json",
            "--print-contract",
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
        timeout=30,
    )
    require(result.returncode == 0, f"--print-contract failed:\n{result.stdout}\n{result.stderr}")

    contract = json.loads(result.stdout)
    require(
        contract.get("authorship_canonical_version") == "trinity.agent_authorship_common.v1",
        f"wrong authorship_canonical_version: {contract.get('authorship_canonical_version')}"
    )

    excluded = contract.get("excluded_dynamic_fields", [])
    require("authorship_proof" in excluded, "authorship_proof must be in excluded_dynamic_fields")

    included = contract.get("included_profile_fields", [])
    require("payload_profile" in included, "payload_profile must be in included_profile_fields")
    require("gateway_intake_fields" in included, "gateway_intake_fields must be in included_profile_fields")
    require("requires_gateway_capabilities" in included, "requires_gateway_capabilities must be in included_profile_fields")
    require("gateway_contract_version" in included, "gateway_contract_version must be in included_profile_fields")
    require("authorship_canonical_version" in included, "authorship_canonical_version must be in included_profile_fields")

    print("PASS: authorship canonical contract is correct")


if __name__ == "__main__":
    main()
