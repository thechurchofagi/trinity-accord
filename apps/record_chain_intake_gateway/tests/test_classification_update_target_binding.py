from apps.record_chain_intake_gateway.gateway.validation import validate_record_type_specific_content


def _draft(target_id: str) -> dict:
    return {
        "authorization_context": {"authorization_scope": "create_classification_update_record"},
        "classification_update_content": {
            "target_record_id": target_id,
            "target_record_sha256": "a" * 64,
            "previous_classification": "old",
            "new_classification": "new",
            "classification_reason": "review",
            "evidence_or_review_basis": "record review",
        },
    }


def test_classification_update_rejects_noncanonical_target_id() -> None:
    diagnostics = validate_record_type_specific_content("classification_update", _draft("not-a-record"))
    assert "INVALID_CLASSIFICATION_TARGET_ID" in {diag.code for diag in diagnostics}


def test_classification_update_accepts_canonical_target_id_shape() -> None:
    diagnostics = validate_record_type_specific_content("classification_update", _draft("R-000000001"))
    assert "INVALID_CLASSIFICATION_TARGET_ID" not in {diag.code for diag in diagnostics}
