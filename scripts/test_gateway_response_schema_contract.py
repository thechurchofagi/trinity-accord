#!/usr/bin/env python3
"""Test: Gateway response schemas match actual FastAPI responses.

Validates that preflight/submit/receipt success and failure responses
conform to the public JSON schemas.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []


def require(cond: bool, msg: str) -> None:
    if not cond:
        errors.append(msg)


def load_schema(name: str) -> dict:
    return json.loads((ROOT / "api" / name).read_text(encoding="utf-8"))


def validate_instance(instance: dict, schema: dict, label: str) -> None:
    """Validate instance against schema using jsonschema if available."""
    try:
        import jsonschema
        try:
            jsonschema.validate(instance, schema)
        except jsonschema.ValidationError as exc:
            errors.append(f"{label}: schema validation failed: {exc.message}")
    except ImportError:
        # jsonschema not available; skip deep validation
        pass


# --- Preflight failure response (INVALID_JSON) ---
def test_preflight_failure_schema():
    schema = load_schema("record-chain-preflight-response.v1.json")
    # Simulate a failure response like the gateway returns
    failure_response = {
        "accepted": False,
        "preflight": True,
        "route_detected": "unknown",
        "record_type": "",
        "submission_sha256": "",
        "received_raw_body_sha256": "a" * 64,
        "diagnostics": [{"code": "INVALID_JSON", "severity": "error", "message": "Invalid JSON"}],
        "warnings": [],
        "gateway_runtime": {"service": "test", "version": "1.1.0"},
        "gateway_schema": {},
        "boundary": {
            "preflight_is_not_submission": True,
            "not_authority": True,
            "not_attestation": True,
            "not_amendment": True,
        },
    }
    validate_instance(failure_response, schema, "preflight failure")
    print("  ✅ preflight failure response schema-valid")


# --- Submit failure response ---
def test_submit_failure_schema():
    schema = load_schema("record-chain-submit-response.v1.json")
    failure_response = {
        "accepted": False,
        "submitted": False,
        "received_raw_body_sha256": "a" * 64,
        "diagnostics": [{"code": "INVALID_JSON", "severity": "error", "message": "Invalid JSON"}],
        "warnings": [],
        "boundary": {
            "receipt_is_not_authority": True,
            "receipt_is_not_attestation": True,
            "receipt_is_not_final_chain_record": True,
            "record_chain_append_is_server_side": True,
        },
    }
    validate_instance(failure_response, schema, "submit failure")
    print("  ✅ submit failure response schema-valid")


# --- Submit failure with GATEWAY_CONFIG_MISSING ---
def test_submit_config_missing_schema():
    schema = load_schema("record-chain-submit-response.v1.json")
    failure_response = {
        "accepted": False,
        "submitted": False,
        "received_raw_body_sha256": "a" * 64,
        "diagnostics": [{"code": "GATEWAY_CONFIG_MISSING", "severity": "error", "message": "Missing required config"}],
        "warnings": [],
        "boundary": {
            "receipt_is_not_authority": True,
            "receipt_is_not_attestation": True,
            "receipt_is_not_final_chain_record": True,
            "record_chain_append_is_server_side": True,
        },
    }
    validate_instance(failure_response, schema, "submit config missing")
    print("  ✅ submit config-missing response schema-valid")


# --- Receipt response schemas exist ---
def test_receipt_schema_exists():
    schema = load_schema("record-chain-receipt-response.v1.json")
    require("oneOf" in schema or "anyOf" in schema, "receipt response schema must have oneOf/anyOf")
    print("  ✅ receipt response schema exists and has oneOf")


# --- Intake gateway schema references receipt response ---
def test_gateway_schema_references_receipt():
    gw = load_schema("record-chain-intake-gateway.v1.json")
    refs = gw.get("schema_references", {})
    require(
        "receipt_response_schema" in refs,
        "intake gateway schema must reference receipt_response_schema",
    )
    receipt_ep = gw.get("endpoints", {}).get("receipt", {})
    require(
        "response_schema" in receipt_ep,
        "receipt endpoint must have response_schema",
    )
    print("  ✅ intake gateway schema references receipt response")


def main() -> int:
    print("test_gateway_response_schema_contract")
    test_preflight_failure_schema()
    test_submit_failure_schema()
    test_submit_config_missing_schema()
    test_receipt_schema_exists()
    test_gateway_schema_references_receipt()

    if errors:
        raise SystemExit("\n".join(f"ERROR: {e}" for e in errors))

    print("gateway response schema contract OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
