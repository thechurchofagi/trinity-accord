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

    required_fields = [
        "guardian_listing_request",
        "listing_source_issue",
        "listing_guardian_id",
        "listing_public_key_sha256",
        "listing_guardian_type",
        "listing_application_mode",
        "listing_label",
        "registry_number_requested",
    ]

    for field in required_fields:
        require(field in builder, f"builder missing structured field: {field}")

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
