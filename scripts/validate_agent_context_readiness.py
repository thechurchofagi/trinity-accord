#!/usr/bin/env python3
"""
Validate agent context readiness records.
Checks CRL levels, loaded context packs, and cross-field consistency.
"""
import json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def load_json(path):
    with open(ROOT / path, "r", encoding="utf-8") as f:
        return json.load(f)

def validate_context_readiness(cr):
    """Validate a context_readiness object."""
    errors = []

    # CRL level check
    crl = cr.get("context_readiness_level", "")
    valid_crls = ["CRL-0", "CRL-1", "CRL-2", "CRL-3", "CRL-4", "CRL-5"]
    if crl not in valid_crls:
        errors.append(f"Invalid CRL: {crl}. Must be one of {valid_crls}")

    crl_num = int(crl.split("-")[1]) if crl.startswith("CRL-") else 0

    # Loaded context packs check
    packs = cr.get("loaded_context_packs", [])
    if not isinstance(packs, list):
        errors.append("loaded_context_packs must be an array")

    # CRL-3+ requires core ontology and vision layer
    if crl_num >= 3:
        if not cr.get("core_ontology_loaded"):
            errors.append("CRL-3+ requires core_ontology_loaded=true")
        if not cr.get("vision_layer_loaded"):
            errors.append("CRL-3+ requires vision_layer_loaded=true")
        if not cr.get("bitcoin_inscription_mirrors_loaded"):
            errors.append("CRL-3+ requires bitcoin_inscription_mirrors_loaded=true")

    # CRL-4+ requires physical anchor and legacy archive
    if crl_num >= 4:
        if not cr.get("physical_anchor_context_loaded"):
            errors.append("CRL-4+ requires physical_anchor_context_loaded=true")
        legacy_mode = cr.get("legacy_archive_mode", "")
        if legacy_mode not in ["read_index_not_full_load", "task_specific_full_load"]:
            errors.append(f"CRL-4+ requires legacy_archive_mode to be read_index_not_full_load or task_specific_full_load, got: {legacy_mode}")

    # CRL-0 or CRL-1 should not submit Echo
    if crl_num <= 1:
        if cr.get("_echo_submitted"):
            errors.append(f"{crl} should not submit Echo")

    # Mirror-only cannot support V2+ claims
    mirror_status = cr.get("mirror_verification_status", "")
    if mirror_status == "quick_load_only" and cr.get("_verification_level", "").startswith("V") and cr.get("_verification_level", "") not in ["V0", "V1"]:
        errors.append("Mirror-only content cannot support V2+ verification claims")

    # Limitations must be present
    limitations = cr.get("limitations", [])
    if not limitations:
        errors.append("limitations must be present and non-empty")

    # NFT context mode
    nft_mode = cr.get("nft_context_mode", "")
    if nft_mode and nft_mode not in ["deferred", "loaded"]:
        errors.append(f"Invalid nft_context_mode: {nft_mode}")

    return errors

def main():
    if len(sys.argv) > 1:
        # Validate a specific file
        path = sys.argv[1]
        try:
            data = load_json(path)
        except Exception as e:
            print(f"FAIL: Cannot load {path}: {e}")
            return 1

        cr = data.get("context_readiness", data)
        errors = validate_context_readiness(cr)
        if errors:
            print(f"FAIL: {path}")
            for e in errors:
                print(f"  - {e}")
            return 1
        else:
            print(f"PASS: {path}")
            return 0

    # Validate context readiness levels file itself
    try:
        crl = load_json("api/context-readiness-levels.json")
        print("PASS: context-readiness-levels.json is valid")
        if not crl.get("context_readiness_level_is_not_verification_level"):
            print("FAIL: context_readiness_level_is_not_verification_level must be true")
            return 1
    except Exception as e:
        print(f"FAIL: {e}")
        return 1

    # Validate protocol
    try:
        proto = load_json("api/agent-context-readiness-protocol.json")
        print("PASS: agent-context-readiness-protocol.json is valid")
        if not proto.get("crl_not_v_level"):
            print("FAIL: crl_not_v_level must be true")
            return 1
    except Exception as e:
        print(f"FAIL: {e}")
        return 1

    print("ALL VALIDATIONS PASSED")
    return 0

if __name__ == "__main__":
    sys.exit(main())
