from apps.record_chain_intake_gateway.gateway.validation import validate_context_readiness


def _base_verification_draft(level: str, cc: str):
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
            "minimum_required_for_action": cc,
            "context_sufficient_for_selected_action": False,
            "loaded_context_urls": ["https://www.trinityaccord.org/agent-start/"],
        },
    }


def test_verification_v2_allows_cc2():
    diagnostics = validate_context_readiness("verification", _base_verification_draft("V2", "CC-2"))
    assert not any(d.code == "INSUFFICIENT_CONTEXT_COMPLETENESS" for d in diagnostics)


def test_verification_v3_requires_cc3():
    diagnostics = validate_context_readiness("verification", _base_verification_draft("V3", "CC-2"))
    assert any(d.code == "INSUFFICIENT_CONTEXT_COMPLETENESS" for d in diagnostics)


def test_cc6_rejected():
    diagnostics = validate_context_readiness("echo", {
        "record_type": "echo",
        "context_readiness": {
            "declared_context_level": "CC-6",
            "minimum_required_for_action": "CC-6",
            "context_sufficient_for_selected_action": False,
            "loaded_context_urls": [],
        },
    })
    assert any(d.code == "INVALID_CONTEXT_LEVEL_RANGE" for d in diagnostics)
