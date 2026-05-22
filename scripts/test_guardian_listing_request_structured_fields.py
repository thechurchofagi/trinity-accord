#!/usr/bin/env python3
"""Ensure Guardian listing request builder and parser support structured fields."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    builder = (ROOT / "scripts" / "build_guardian_listing_request_payload.py").read_text(encoding="utf-8")
    parser = (ROOT / "scripts" / "auto_register_guardian_from_gateway_issues.py").read_text(encoding="utf-8")

    # Builder must emit structured fields in the guardian_listing_request section
    # The builder constructs a JSON payload, so fields are at nested level
    required_builder_fields = [
        "guardian_listing_request",
        "source_issue",
        "guardian_id",
        "public_key_sha256",
        "guardian_type",
        "application_mode",
        "label",
        "registry_number_requested",
    ]

    for field in required_builder_fields:
        require(field in builder, f"builder missing field: {field}")

    # Parser must read structured fields first from intake block
    for field in [
        'fields.get("listing_guardian_id")',
        'fields.get("listing_public_key_sha256")',
        'fields.get("listing_guardian_type")',
        'fields.get("listing_application_mode")',
        'fields.get("listing_label")',
        'fields.get("listing_source_issue")',
    ]:
        require(field in parser, f"auto-register parser missing structured field read: {field}")

    print("GUARDIAN_LISTING_REQUEST_STRUCTURED_FIELDS_OK")


if __name__ == "__main__":
    main()
