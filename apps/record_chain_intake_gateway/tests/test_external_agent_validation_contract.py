from __future__ import annotations

from apps.record_chain_intake_gateway.gateway.validation import (
    validate_context_readiness,
    validate_provenance_semantics,
    validate_record_type_specific_content,
)


def codes(diags):
    return {item.code for item in diags}


def test_direct_verification_requires_multidimensional_claim_model():
    draft = {
        "authorization_context": {"authorization_scope": "create_verification_record"},
        "verification_content": {
            "verification_level": "V3",
            "what_was_checked": ["hashes"],
            "verification_claim": "bounded",
            "fresh_actions_performed": ["read"],
        },
    }
    assert "MISSING_VERIFICATION_CLAIM_MODEL" in codes(
        validate_record_type_specific_content("verification", draft)
    )


def test_direct_cc3_rejects_whitespace_url():
    draft = {
        "context_readiness": {
            "declared_context_level": "CC-3",
            "context_sufficient_for_selected_action": True,
            "loaded_context_urls": [" https://www.trinityaccord.org/agent-start/"],
        }
    }
    result = codes(validate_context_readiness("echo", draft))
    assert "INVALID_LOADED_CONTEXT_URL" in result


def test_agent_request_party_requires_agent_request_boolean():
    draft = {
        "decision_autonomy_context": {
            "who_decided_to_create_this_record": "mixed",
            "was_record_creation_self_decided": False,
            "was_record_creation_requested_by_human": False,
            "was_record_creation_requested_by_another_agent": False,
            "requesting_party_type": "agent",
        }
    }
    assert "PROVENANCE_REQUEST_FLAG_MISMATCH" in codes(validate_provenance_semantics(draft))
