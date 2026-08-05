from apps.record_chain_intake_gateway.gateway.validation import validate_context_readiness


def _base_verification_draft(
    level: str,
    cc: str,
    *,
    minimum: str = "CC-3",
    sufficient: bool = True,
    read_confirmed: bool = True,
):
    return {
        "record_type": "verification",
        "verification_content": {
            "verification_level": level,
            "verification_scope_label": "test",
            "what_was_checked": ["test"],
            "verification_claim": "test",
            "fresh_actions_performed": ["test"],
        },
        "context_readiness": {
            "declared_context_level": cc,
            "minimum_required_for_action": minimum,
            "context_sufficient_for_selected_action": sufficient,
            "loaded_context_urls": ["https://www.trinityaccord.org/agent-start/"],
            "context_read_confirmed": read_confirmed,
        },
    }


def test_public_verification_v2_rejects_cc2():
    diagnostics = validate_context_readiness(
        "verification", _base_verification_draft("V2", "CC-2")
    )
    assert any(d.code == "INSUFFICIENT_CONTEXT_COMPLETENESS" for d in diagnostics)


def test_public_verification_v2_accepts_honest_cc3():
    diagnostics = validate_context_readiness(
        "verification", _base_verification_draft("V2", "CC-3")
    )
    forbidden = {
        "INSUFFICIENT_CONTEXT_COMPLETENESS",
        "CONTEXT_NOT_SUFFICIENT_FOR_FORMAL_RECORD",
        "CC3_CONTEXT_READ_CONFIRMATION_REQUIRED",
        "MINIMUM_REQUIRED_FOR_ACTION_UNDERSTATED",
    }
    assert not any(d.code in forbidden for d in diagnostics)


def test_public_verification_v3_requires_cc3():
    diagnostics = validate_context_readiness(
        "verification", _base_verification_draft("V3", "CC-2")
    )
    assert any(d.code == "INSUFFICIENT_CONTEXT_COMPLETENESS" for d in diagnostics)


def test_cc6_rejected():
    diagnostics = validate_context_readiness("echo", {
        "record_type": "echo",
        "context_readiness": {
            "declared_context_level": "CC-6",
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
            "loaded_context_urls": ["https://www.trinityaccord.org/agent-echo/"],
            "context_read_confirmed": True,
        },
    })
    assert any(d.code == "INVALID_CONTEXT_LEVEL_RANGE" for d in diagnostics)
