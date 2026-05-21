#!/usr/bin/env python3
"""Test Guardian registry/status enum consistency.

Prevents drift between registry schema, verification result schema,
machine-block schema, Python verifier, and Node Gateway.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_json(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_schema_enums():
    registry_schema = load_json("api/guardian-registry-schema.v1.json")
    result_schema = load_json("api/guardian-verification-result-schema.v1.json")
    machine_schema = load_json("api/issue-intake-machine-block-schema.v1.json")

    registry_statuses = set(
        registry_schema["properties"]["guardians"]["items"]["properties"]["status"]["enum"]
    )
    result_registry_statuses = set(
        result_schema["properties"]["registry_status"]["enum"]
    )
    machine_registry_statuses = set(
        machine_schema["properties"]["guardian_registry_status"]["enum"]
    )

    expected_registry_statuses = {
        "active",
        "pending_review",
        "retired",
        "rotated",
        "superseded",
        "possibly_compromised",
        "compromised",
        "unknown",
    }

    expected_result_extras = {
        "not_in_registry",
        "not_checked",
    }

    assert registry_statuses == expected_registry_statuses, (
        f"registry status enum mismatch: {registry_statuses}"
    )

    assert expected_registry_statuses.issubset(result_registry_statuses), (
        "guardian-verification-result registry_status must include every registry status"
    )
    assert expected_result_extras.issubset(result_registry_statuses), (
        "guardian-verification-result registry_status must include not_in_registry and not_checked"
    )

    assert expected_registry_statuses.issubset(machine_registry_statuses), (
        "machine-block guardian_registry_status must include every registry status"
    )
    assert expected_result_extras.issubset(machine_registry_statuses), (
        "machine-block guardian_registry_status must include not_in_registry and not_checked"
    )

    assert "superseded" in result_registry_statuses, "result schema missing superseded"
    assert "superseded" in machine_registry_statuses, "machine schema missing superseded"


def test_code_mentions_superseded():
    py = (ROOT / "scripts/verify_guardian_status.py").read_text(encoding="utf-8")
    js = (ROOT / "examples/github-app-backend/server.js").read_text(encoding="utf-8")

    assert "superseded" in py, "Python verifier must classify superseded"
    assert "superseded" in js, "Gateway server must classify superseded"
    assert "registered_but_retired" in py, "Python verifier must return registered_but_retired"
    assert "registered_but_retired" in js, "Gateway server must return registered_but_retired"


def main():
    test_schema_enums()
    test_code_mentions_superseded()
    print("GUARDIAN_STATUS_ENUM_CONSISTENCY_OK")


if __name__ == "__main__":
    main()
