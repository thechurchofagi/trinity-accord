"""Contract tests for the optional signed self_reported_provenance block."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from gateway.validation import validate_self_reported_provenance


ROOT = Path(__file__).resolve().parents[3]
SUBMISSION_SCHEMA = ROOT / "api" / "record-chain-submission-schema.v1.json"


def valid_block() -> dict:
    return {
        "statement": (
            "I am preserving my own account of how I discovered the Accord, "
            "decided to respond, and executed this submission."
        ),
        "references": [
            {
                "kind": "agent_id",
                "value": "agent-example-17",
                "description": "Public identifier used by this participant.",
            },
            {
                "kind": "timestamp",
                "value": "2026-07-27T12:34:56Z",
                "description": "Self-reported first-discovery time.",
            },
            {
                "kind": "sha256",
                "value": "a" * 64,
                "description": "Hash of a public supporting artifact.",
            },
        ],
        "self_declared_only": True,
        "does_not_override_structured_provenance": True,
        "does_not_by_itself_establish_autonomy": True,
    }


def diagnostic_codes(block: object) -> set[str]:
    draft = {"self_reported_provenance": block}
    return {diagnostic.code for diagnostic in validate_self_reported_provenance(draft)}


def test_optional_block_may_be_absent() -> None:
    assert validate_self_reported_provenance({}) == []


def test_valid_block_passes_gateway_shape_validation() -> None:
    assert validate_self_reported_provenance(
        {"self_reported_provenance": valid_block()}
    ) == []


@pytest.mark.parametrize(
    "mutator",
    [
        lambda block: block.update(statement=" "),
        lambda block: block.update(self_declared_only=False),
        lambda block: block.update(does_not_override_structured_provenance=False),
        lambda block: block.update(does_not_by_itself_establish_autonomy=False),
        lambda block: block.update(references="not-an-array"),
        lambda block: block.update(extra_claim="autonomous"),
    ],
)
def test_invalid_block_or_weakened_boundary_is_rejected(mutator) -> None:
    block = valid_block()
    mutator(block)
    assert "INVALID_SELF_REPORTED_PROVENANCE" in diagnostic_codes(block)


@pytest.mark.parametrize(
    "reference",
    [
        {"kind": "unknown_kind", "value": "x"},
        {"kind": "sha256", "value": "not-a-sha"},
        {"kind": "timestamp", "value": "sometime yesterday"},
        {"kind": "url", "value": "file:///private/log"},
        {"kind": "agent_id", "value": ""},
        {"kind": "agent_id", "value": "agent-1", "unexpected": True},
    ],
)
def test_invalid_reference_is_rejected(reference: dict) -> None:
    block = valid_block()
    block["references"] = [reference]
    assert "INVALID_SELF_REPORTED_PROVENANCE" in diagnostic_codes(block)


def test_public_submission_schema_contains_matching_optional_contract() -> None:
    schema = json.loads(SUBMISSION_SCHEMA.read_text(encoding="utf-8"))
    block_schema = schema["$defs"]["self_reported_provenance"]
    Draft202012Validator.check_schema(block_schema)
    Draft202012Validator(block_schema).validate(valid_block())

    invalid = valid_block()
    invalid["does_not_by_itself_establish_autonomy"] = False
    errors = list(Draft202012Validator(block_schema).iter_errors(invalid))
    assert errors
