from __future__ import annotations

from gateway.validation import validate_context_readiness


def codes(record_type: str, context: dict, *, verification_level: str | None = None) -> set[str]:
    draft: dict = {"context_readiness": context}
    if verification_level is not None:
        draft["verification_content"] = {"verification_level": verification_level}
    return {item.code for item in validate_context_readiness(record_type, draft)}


def valid_cc3() -> dict:
    return {
        "declared_context_level": "CC-3",
        "minimum_required_for_action": "CC-3",
        "context_sufficient_for_selected_action": True,
        "context_read_confirmed": True,
        "loaded_context_urls": [
            "https://www.trinityaccord.org/authority/",
            "https://www.trinityaccord.org/agent-brief/",
        ],
    }


def test_public_echo_and_verification_require_cc3() -> None:
    cc2 = {
        "declared_context_level": "CC-2",
        "minimum_required_for_action": "CC-2",
        "context_sufficient_for_selected_action": True,
        "loaded_context_urls": ["https://www.trinityaccord.org/authority/"],
    }
    assert "INSUFFICIENT_CONTEXT_COMPLETENESS" in codes("echo", cc2)
    assert "INSUFFICIENT_CONTEXT_COMPLETENESS" in codes("verification", cc2, verification_level="V2")
    assert "INSUFFICIENT_CONTEXT_COMPLETENESS" not in codes("verification", valid_cc3(), verification_level="V2")


def test_formal_record_rejects_self_declared_insufficiency() -> None:
    context = valid_cc3()
    context["context_sufficient_for_selected_action"] = False
    assert "CONTEXT_NOT_SUFFICIENT_FOR_FORMAL_RECORD" in codes("echo", context)


def test_cc3_requires_explicit_read_confirmation() -> None:
    context = valid_cc3()
    context.pop("context_read_confirmed")
    assert "CC3_CONTEXT_READ_CONFIRMATION_REQUIRED" in codes("echo", context)


def test_gateway_rejects_understated_minimum() -> None:
    context = valid_cc3()
    context["minimum_required_for_action"] = "CC-1"
    assert "MINIMUM_REQUIRED_FOR_ACTION_UNDERSTATED" in codes("echo", context)


def test_higher_conservative_minimum_is_not_understatement() -> None:
    context = valid_cc3()
    context["declared_context_level"] = "CC-4"
    context["minimum_required_for_action"] = "CC-4"
    assert "MINIMUM_REQUIRED_FOR_ACTION_UNDERSTATED" not in codes("propagation", context)
