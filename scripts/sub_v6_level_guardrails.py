#!/usr/bin/env python3
"""Warning-only guardrails for sub-V6 agent-declared template levels.

These warnings help prevent accidental level misselection.
They do not block V0–V5 archive creation.
"""

V0_V5_LEVELS = {"V0", "V1", "V2", "V3", "V4", "V4+", "V5"}
HIGH_SUB_V6_LEVELS = {"V4", "V4+", "V5"}


def sub_v6_level_selection_acknowledgement(level):
    return {
        "declared_template_level": level,
        "understands_self_declared_template_level": True,
        "understands_evidence_waived_for_v0_v5": True,
        "understands_not_strict_evidence_verification": True,
        "understands_not_formal_attestation": True,
        "understands_should_choose_lower_if_uncertain": True,
        "confirmed_what_i_checked_and_limitations_are_accurate": True,
    }


def high_level_confirmation(level):
    if level in HIGH_SUB_V6_LEVELS:
        return {
            "required": True,
            "agent_confirmed_high_level_self_selection": True,
            "agent_confirmed_no_strict_v6plus_claim": True,
            "agent_confirmed_limitations_disclosed": True,
        }
    return {
        "required": False,
    }


def collect_sub_v6_level_selection_warnings(payload):
    """Return warning strings for V0-V5 declared template level selection.

    Does not block archive creation. Intended to prevent accidental level misselection.
    """
    level = (
        payload.get("agent_declared_protocol_level")
        or payload.get("verification_level_claimed")
        or (payload.get("claim_gate") or {}).get("allowed_protocol_level")
        or ""
    )

    if level not in V0_V5_LEVELS:
        return []

    if payload.get("requested_archive_kind") != "agent_declared_verification_archive":
        return []

    what = payload.get("what_i_checked") or []
    lims = payload.get("limitations") or []
    text = " ".join(str(x) for x in (what + lims)).lower()

    def has_any(words):
        return any(w.lower() in text for w in words)

    warnings = []

    if level in {"V4", "V4+", "V5"} and not has_any([
        "script", "scripts", "run", "review", "check_consistency", "verify.py",
        "verify_bitcoin_inscription_mirrors", "source read", "source reviewed"
    ]):
        warnings.append(
            "Declared high sub-V6 template level but what_i_checked does not mention script review/run. "
            "This is allowed in evidence-waived template mode, but confirm the level was intentional."
        )

    if level in {"V3", "V4", "V4+", "V5"} and not has_any([
        "hash", "sha-256", "sha256", "digest", "content comparison", "computed"
    ]):
        warnings.append(
            "Declared V3+ template level but what_i_checked does not mention hash/digest/content comparison. "
            "Evidence is waived for V0–V5, but confirm the level was intentional."
        )

    if level == "V5" and not has_any([
        "digital", "mirror", "mirrors", "arweave", "ipfs", "eth", "ethereum",
        "bitcoin", "chronicle", "time anchor", "public digital"
    ]):
        warnings.append(
            "Declared V5 template level but what_i_checked does not mention broad public digital review. "
            "This may be intentional, but confirm this is not a mistaken level selection."
        )

    if level in {"V3", "V4", "V4+", "V5"} and has_any([
        "no hash", "hash not computed", "did not compute hash", "no digest"
    ]):
        warnings.append(
            "Limitations appear to say no hash/digest was computed while declared level is V3+. "
            "This may still be valid as an oath-bound template declaration, but should be confirmed."
        )

    if level in {"V4+", "V5"} and has_any([
        "did not independently reproduce", "no independent reproduction", "not independently recovered"
    ]):
        warnings.append(
            "Limitations mention missing independent reproduction while declared level is V4+ or V5. "
            "This may be a limited self-declaration, but public display should remain agent-declared template level."
        )

    ack = payload.get("level_selection_acknowledgement") or {}
    if not ack:
        warnings.append(
            "Missing level_selection_acknowledgement. Future builder versions should include it."
        )
    else:
        required_true = [
            "understands_self_declared_template_level",
            "understands_evidence_waived_for_v0_v5",
            "understands_not_strict_evidence_verification",
            "understands_not_formal_attestation",
            "confirmed_what_i_checked_and_limitations_are_accurate",
        ]
        for key in required_true:
            if ack.get(key) is not True:
                warnings.append(f"level_selection_acknowledgement.{key} should be true")

    if level in {"V4", "V4+", "V5"}:
        high = payload.get("high_level_confirmation") or {}
        if high.get("required") is not True:
            warnings.append("high_level_confirmation.required should be true for V4/V4+/V5")
        for key in [
            "agent_confirmed_high_level_self_selection",
            "agent_confirmed_no_strict_v6plus_claim",
            "agent_confirmed_limitations_disclosed",
        ]:
            if high.get(key) is not True:
                warnings.append(f"high_level_confirmation.{key} should be true for V4/V4+/V5")

    return warnings


def sub_v6_level_selection_lint(payload):
    return {
        "mode": "warning_only",
        "warnings": collect_sub_v6_level_selection_warnings(payload),
        "warnings_block_archive": False,
        "purpose": "Prevent accidental level misselection and terminology confusion.",
        "does_not_require_evidence_chain": True,
    }
