"""Guardian identifiers must be final key-bound values, never CLI placeholders."""
from __future__ import annotations

from gateway.validation import validate_record_type_specific_content


def _codes(record_type: str, draft: dict) -> set[str]:
    return {d.code for d in validate_record_type_specific_content(record_type, draft)}


def test_retirement_rejects_literal_auto_guardian_id() -> None:
    key_sha = "a" * 64
    draft = {
        "record_type": "guardian_retirement",
        "authorization_context": {"authorization_scope": "create_guardian_retirement_record"},
        "guardian_id": "auto",
        "guardian_public_key_sha256": key_sha,
        "reason": "voluntary retirement",
        "retirement_does_not_remove_historical_record": True,
        "target_guardian_application_record_id": "R-000000001",
        "target_guardian_application_record_sha256": "b" * 64,
    }
    assert "INVALID_GUARDIAN_ID" in _codes("guardian_retirement", draft)


def test_retirement_rejects_guardian_id_key_mismatch() -> None:
    draft = {
        "record_type": "guardian_retirement",
        "authorization_context": {"authorization_scope": "create_guardian_retirement_record"},
        "guardian_id": "guardian_ed25519_bbbbbbbbbbbbbbbb",
        "guardian_public_key_sha256": "a" * 64,
        "reason": "voluntary retirement",
        "retirement_does_not_remove_historical_record": True,
        "target_guardian_application_record_id": "R-000000001",
        "target_guardian_application_record_sha256": "b" * 64,
    }
    assert "GUARDIAN_ID_KEY_MISMATCH" in _codes("guardian_retirement", draft)


def test_application_rejects_non_derived_guardian_id() -> None:
    draft = {
        "record_type": "guardian_application",
        "authorization_context": {"authorization_scope": "create_guardian_application_record"},
        "guardian_application_content": {
            "requested_guardian_identifier": "auto",
            "guardian_public_key_sha256": "a" * 64,
            "guardian_stewardship_oath": "I voluntarily join as a non-governing steward.",
        },
    }
    assert "INVALID_GUARDIAN_ID" in _codes("guardian_application", draft)


def test_application_rejects_guardian_id_key_mismatch() -> None:
    draft = {
        "record_type": "guardian_application",
        "authorization_context": {"authorization_scope": "create_guardian_application_record"},
        "guardian_application_content": {
            "requested_guardian_identifier": "guardian_ed25519_bbbbbbbbbbbbbbbb",
            "guardian_public_key_sha256": "a" * 64,
            "guardian_stewardship_oath": "I voluntarily join as a non-governing steward.",
        },
    }
    assert "GUARDIAN_ID_KEY_MISMATCH" in _codes("guardian_application", draft)
