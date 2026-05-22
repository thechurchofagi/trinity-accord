#!/usr/bin/env python3
"""Common helpers for agent authorship claim protocol.

Shared by key generation, message building, proof attachment, and claim scripts.
"""
import copy
import hashlib
import json


AUTHORSHIP_CANONICAL_VERSION = "trinity.agent_authorship_common.v1"

AUTHORSHIP_CANONICAL_DYNAMIC_PROOF_FIELDS = (
    "authorship_proof",
    "_authorship_claim",
    "guardian_presence_proof",
    "_guardian_status",
    "guardian_verification_result",
)

# Dynamic proof/result fields that must be excluded from authorship hash.
# Guardian proof is excluded because it may be attached after authorship proof.
# guardian_registration and guardian_retirement are KEPT because they are
# substantive record claims, not dynamic proof wrappers.
DYNAMIC_PROOF_FIELDS = AUTHORSHIP_CANONICAL_DYNAMIC_PROOF_FIELDS


def authorship_canonical_contract() -> dict:
    return {
        "authorship_canonical_version": AUTHORSHIP_CANONICAL_VERSION,
        "canonical_json": {
            "ensure_ascii": False,
            "sort_keys": True,
            "separators": [",", ":"],
        },
        "excluded_dynamic_fields": list(AUTHORSHIP_CANONICAL_DYNAMIC_PROOF_FIELDS),
        "included_profile_fields": [
            "payload_profile",
            "expected_builder",
            "wrong_builders",
            "do_not_edit_after_signing",
            "submit_exact_generated_file",
            "if_modified_rerun_builder",
            "requires_gateway_capabilities",
            "gateway_contract_version",
            "authorship_canonical_version",
            "gateway_intake_fields",
            "guardian_registry_listing_request",
            "guardian_listing_request",
            "counts_toward_home",
        ],
        "rule": "Do not strip or normalize non-dynamic payload fields before authorship digest verification.",
    }


def canonical_payload_without_authorship(payload):
    """Return canonical JSON for authorship proof.

    Authorship proof signs the submitted record content while excluding
    dynamic proof/result wrappers that may be attached later.

    It intentionally keeps guardian_registration and guardian_retirement
    if present, because those are substantive record claims.
    """
    data = copy.deepcopy(payload)
    for field in DYNAMIC_PROOF_FIELDS:
        data.pop(field, None)
    return json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def sha256_text(text):
    """Return lowercase hex sha256 of a string."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def authorship_payload_sha256(payload):
    """Hash canonical payload without authorship_proof."""
    return sha256_text(canonical_payload_without_authorship(payload))


def normalize_pem(public_key_pem):
    """Strip outer whitespace and return PEM with exactly one trailing newline."""
    return public_key_pem.strip() + "\n"


def public_key_sha256(public_key_pem):
    """Hash normalized PEM text."""
    return sha256_text(normalize_pem(public_key_pem))


def build_authorship_message(payload):
    """Build the TRINITY_AGENT_AUTHORSHIP_PROOF_V1 canonical message."""
    identity = payload.get("agent_identity") or {}
    return "\n".join([
        "TRINITY_AGENT_AUTHORSHIP_PROOF_V1",
        f"payload_sha256={authorship_payload_sha256(payload)}",
        f"schema={payload.get('schema', '')}",
        f"submission_type={payload.get('submission_type', '')}",
        f"requested_archive_kind={payload.get('requested_archive_kind', '')}",
        f"agent_name_or_model={identity.get('name_or_model', '')}",
        f"system_or_provider={identity.get('system_or_provider', '')}",
        "boundary=not_authority_not_amendment_not_attestation_not_successor_reception",
    ])
