#!/usr/bin/env python3
"""Ensure first active Guardian 00001 is public, documented, and stable."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED = {
    "guardian_registry_number": "00001",
    "guardian_id": "guardian_ed25519_6910213445feadea",
    "public_key_sha256": "6910213445feadea50c0d0e066fc477434be6235e0f26543e1c31b0ec1154536",
    "algorithm": "ed25519",
    "status": "active",
    "guardian_type": "human_with_ai_agent",
    "application_mode": "joint_human_ai",
    "source_issue": 227,
    "listing_request_issue": 228,
    "listed_at": "2026-05-22",
    "label": "Hongju Liu + 守望者",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def main():
    registry = json.loads(read("api/guardian-registry.json"))
    guardians = registry.get("guardians", [])

    matches = [
        g for g in guardians
        if g.get("guardian_registry_number") == EXPECTED["guardian_registry_number"]
    ]

    require(len(matches) == 1, "Expected exactly one Guardian with registry number 00001")

    entry = matches[0]
    for key, value in EXPECTED.items():
        require(entry.get(key) == value, f"Guardian 00001 field mismatch for {key}: got {entry.get(key)!r}, expected {value!r}")

    require(entry.get("boundary", {}).get("not_authority") is True, "Guardian 00001 boundary.not_authority must be true")
    require(entry.get("boundary", {}).get("not_governance") is True, "Guardian 00001 boundary.not_governance must be true")
    require(entry.get("boundary", {}).get("not_attestation") is True, "Guardian 00001 boundary.not_attestation must be true")
    require(entry.get("boundary", {}).get("not_verification_level") is True, "Guardian 00001 boundary.not_verification_level must be true")
    require(entry.get("boundary", {}).get("bitcoin_originals_prevail") is True, "Guardian 00001 boundary.bitcoin_originals_prevail must be true")

    public_docs = {
        "guardian-alliance.md": read("guardian-alliance.md"),
        "guardian-join.md": read("guardian-join.md"),
        "README.md": read("README.md"),
        "llms.txt": read("llms.txt"),
    }

    for path, content in public_docs.items():
        require("00001" in content, f"{path} must mention active Guardian number 00001")
        require(EXPECTED["guardian_id"] in content, f"{path} must mention Guardian ID {EXPECTED['guardian_id']}")
        require("active_registered_guardian" in content, f"{path} must mention active_registered_guardian")
        require("/api/guardian-registry.json" in content, f"{path} must link or refer to /api/guardian-registry.json")

    combined = "\n".join(public_docs.values())
    # Private key files should not be suggested as commit targets
    for line in combined.split("\n"):
        line_lower = line.lower().strip()
        if "private.pem" in line_lower and ("commit" in line_lower or "push" in line_lower or "add" in line_lower):
            if "do not" not in line_lower and "don't" not in line_lower and "never" not in line_lower and "must not" not in line_lower:
                require(False, f"Public docs must not suggest committing private key files: {line.strip()}")

    print("GUARDIAN_00001_PUBLIC_FINALIZATION_OK")


if __name__ == "__main__":
    main()
