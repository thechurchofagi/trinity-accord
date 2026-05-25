#!/usr/bin/env python3
"""Semantic validation for Gateway payloads beyond JSON Schema."""
import argparse
import hashlib
import json
import sys
from pathlib import Path


def validate(payload: dict) -> list[str]:
    errors = []

    kind = payload.get("requested_archive_kind")

    # --- Level consistency ---
    if kind == "agent_declared_verification_archive":
        declared = payload.get("agent_declared_protocol_level")
        ack = (payload.get("level_selection_acknowledgement") or {}).get("declared_template_level")
        if ack is not None and declared != ack:
            errors.append(
                "agent_declared_protocol_level must equal "
                "level_selection_acknowledgement.declared_template_level"
            )

        # Claim Gate validation
        claim_gate = payload.get("claim_gate")
        if not isinstance(claim_gate, dict):
            errors.append("agent_declared_verification_archive requires non-null claim_gate object")
        else:
            allowed_statuses = {"PASS", "PASS_WITH_WARNINGS", "PASS_WITH_DOWNGRADE"}
            if claim_gate.get("status") not in allowed_statuses:
                errors.append(
                    "agent_declared_verification_archive requires claim_gate.status to be "
                    "PASS/PASS_WITH_WARNINGS/PASS_WITH_DOWNGRADE"
                )
            if claim_gate.get("mode") != "template_for_v0_v5":
                errors.append(
                    "agent_declared_verification_archive requires claim_gate.mode=template_for_v0_v5"
                )
            if claim_gate.get("allowed_protocol_level") != declared:
                errors.append("claim_gate.allowed_protocol_level must equal agent_declared_protocol_level")

    # --- Echo archive constraints ---
    if kind == "agent_declared_echo_archive":
        if payload.get("agent_declared_protocol_level"):
            errors.append("agent_declared_echo_archive must not claim agent_declared_protocol_level")
        if payload.get("verification_level_claimed"):
            errors.append("agent_declared_echo_archive must not claim verification_level_claimed")
        counts = payload.get("counts_toward_home") or {}
        if counts.get("verifiability") is not False:
            errors.append("agent_declared_echo_archive counts_toward_home.verifiability must be false")
        if counts.get("reception") is not True:
            errors.append("agent_declared_echo_archive counts_toward_home.reception must be true")

    # --- Guardian listing constraints ---
    if payload.get("guardian_registry_listing_request") is True:
        if kind != "guardian_active_registry_listing_request":
            errors.append(
                "guardian_registry_listing_request requires "
                "requested_archive_kind=guardian_active_registry_listing_request"
            )
        if payload.get("echo_type") != "E6_propagation_echo":
            errors.append("guardian_registry_listing_request requires echo_type=E6_propagation_echo")
        if payload.get("guardian_presence_proof") is not None:
            errors.append("guardian_registry_listing_request must not include guardian_presence_proof")

    # --- Authority boundary content ---
    archive_kinds_requiring_boundary = {
        "agent_declared_verification_archive",
        "agent_declared_echo_archive",
        "guardian_active_registry_listing_request",
    }

    if kind in archive_kinds_requiring_boundary:
        boundary = payload.get("authority_boundary")
        if not isinstance(boundary, dict):
            errors.append("authority_boundary must be a non-null object")
        else:
            for key in [
                "bitcoin_originals_remain_final",
                "does_not_amend_bitcoin_originals",
                "does_not_override_bitcoin_originals",
            ]:
                if boundary.get(key) is not True:
                    errors.append(f"authority_boundary.{key} must be true")

        # Non-empty content arrays
        for key in ["what_i_checked", "limitations"]:
            items = payload.get(key)
            if not isinstance(items, list) or not items:
                errors.append(f"{key} must contain at least one non-empty item")
            elif any(not isinstance(x, str) or not x.strip() for x in items):
                errors.append(f"{key} must contain only non-empty strings")

    # --- Readback hash verification ---
    oath = ((payload.get("agent_integrity_declaration") or {}).get("verification_oath") or {})
    readback = oath.get("agent_readback")
    readback_hash = oath.get("agent_readback_sha256")
    if readback is not None and readback_hash is not None:
        actual = hashlib.sha256(readback.encode("utf-8")).hexdigest()
        if readback_hash != actual:
            errors.append("agent_readback_sha256 does not match agent_readback")

    if kind in {"agent_declared_echo_archive", "guardian_active_registry_listing_request"}:
        if payload.get("evidence_requirement_mode") != "not_applicable_for_echo":
            errors.append(f"{kind} requires evidence_requirement_mode=not_applicable_for_echo")
    if kind == "agent_declared_verification_archive":
        if payload.get("evidence_requirement_mode") != "waived_for_v0_v5":
            errors.append("agent_declared_verification_archive requires evidence_requirement_mode=waived_for_v0_v5")

    if kind in {"agent_declared_echo_archive", "agent_declared_verification_archive", "guardian_active_registry_listing_request"}:
        discovery = payload.get("discovery_provenance")
        if not isinstance(discovery, dict):
            errors.append("discovery_provenance must be a non-null object")
        elif not str(discovery.get("source", "")).strip():
            errors.append("discovery_provenance.source must be a non-empty string")

    if kind == "agent_declared_verification_archive":
        claim_gate = payload.get("claim_gate")
        if isinstance(claim_gate, dict):
            components = claim_gate.get("allowed_component_levels")
            if components is not None:
                if not isinstance(components, dict):
                    errors.append("claim_gate.allowed_component_levels must be an object when present")
                else:
                    allowed_component_keys = {"context_depth", "evidence_depth", "tool_reproduction", "independence"}
                    unknown = sorted(set(components) - allowed_component_keys)
                    if unknown:
                        errors.append(f"claim_gate.allowed_component_levels contains unknown keys: {unknown}")

    if kind in {"agent_declared_verification_archive", "agent_declared_echo_archive", "guardian_active_registry_listing_request"}:
        identity = payload.get("agent_identity") or {}
        if identity.get("self_reported") is not True:
            level = identity.get("identity_verification_level")
            if level not in {"signed_statement", "institutional_domain", "notarial_identity"}:
                errors.append("agent_identity.self_reported=false requires signed_statement, institutional_domain, or notarial_identity")
            if not payload.get("authorship_proof"):
                errors.append("agent_identity.self_reported=false requires authorship_proof")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("payload", nargs="+", help="Gateway payload JSON file(s)")
    args = parser.parse_args()

    ok = True
    for path_text in args.payload:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        errors = validate(payload)
        if errors:
            ok = False
            print(f"FAIL: {path}")
            for e in errors:
                print(f"  - {e}")
        else:
            print(f"PASS: {path}")

    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
