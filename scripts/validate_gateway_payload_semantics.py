#!/usr/bin/env python3
"""Semantic validation for Gateway payloads beyond JSON Schema."""
import argparse
import json
import sys
from pathlib import Path


def validate(payload: dict) -> list[str]:
    errors = []

    kind = payload.get("requested_archive_kind")

    if kind == "agent_declared_verification_archive":
        declared = payload.get("agent_declared_protocol_level")
        ack = (payload.get("level_selection_acknowledgement") or {}).get("declared_template_level")
        if ack is not None and declared != ack:
            errors.append(
                "agent_declared_protocol_level must equal "
                "level_selection_acknowledgement.declared_template_level"
            )

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

    if payload.get("guardian_registry_listing_request") is True:
        if kind != "guardian_active_registry_listing_request":
            errors.append("guardian_registry_listing_request requires requested_archive_kind=guardian_active_registry_listing_request")
        if payload.get("echo_type") != "E6_propagation_echo":
            errors.append("guardian_registry_listing_request requires echo_type=E6_propagation_echo")
        if payload.get("guardian_presence_proof") is not None:
            errors.append("guardian_registry_listing_request must not include guardian_presence_proof")

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
