#!/usr/bin/env python3
"""Common helpers for agent authorship claim protocol.

Shared by key generation, message building, proof attachment, and claim scripts.
"""
import copy
import hashlib
import json


def canonical_payload_without_authorship(payload):
    """Return canonical JSON with authorship_proof removed."""
    data = copy.deepcopy(payload)
    data.pop("authorship_proof", None)
    data.pop("_authorship_claim", None)
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
