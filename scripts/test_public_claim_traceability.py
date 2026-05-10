#!/usr/bin/env python3
"""Test public claim traceability (TA-REDTEAM-2026-017).

Checks that claim registry exists, covers required claims, and public surfaces reference it.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CLAIM_IDS = {
    "bitcoin_originals_are_canonical",
    "github_pages_are_non_amending_mirror",
    "btc_signature_binds_authority_manifest",
    "eth_witness_is_secondary",
    "digest_manifest_covers_evidence_integrity",
    "release_pass_requires_corrections_index",
    "echo_records_do_not_count_as_attestation",
    "formal_attestation_requires_positive_gates",
    "notarized_evidence_is_not_formal_attestation",
    "recovery_is_clean_room_executable",
    "github_free_verifier_bundle_is_deferred",
    "nft_car_backups_are_recovery_mirrors_not_authority",
    "scarcity_claim_is_framing_not_proof",
}


def main():
    errors = []

    # 1. Registry exists
    registry_path = ROOT / "api" / "claim-registry.json"
    if not registry_path.exists():
        errors.append("api/claim-registry.json does not exist")
        print(f"FAIL: {errors}")
        sys.exit(1)

    data = json.loads(registry_path.read_text())
    claims = data.get("claims", [])
    claim_ids = {c["claim_id"] for c in claims}

    # 2. Required claim IDs
    for rid in REQUIRED_CLAIM_IDS:
        if rid not in claim_ids:
            errors.append(f"Missing required claim_id: {rid}")

    # 3. Every current/complete claim has required fields
    for claim in claims:
        cs = claim.get("current_status", "current")
        ts = claim.get("traceability_status", "complete")
        if cs in ("deferred", "planned") or ts in ("deferred",):
            continue
        cid = claim["claim_id"]
        for field in ["public_surfaces", "source_files", "limitations", "does_not_prove", "corrections_path", "validators"]:
            if not claim.get(field):
                errors.append(f"Claim {cid}: {field} is empty or missing")

    # 4. Public surfaces reference claim registry
    llms = (ROOT / "llms.txt").read_text()
    if "claim" not in llms.lower() or "registry" not in llms.lower():
        errors.append("llms.txt does not reference claim registry")

    ai = (ROOT / "ai.txt").read_text()
    if "claim" not in ai.lower() or "registry" not in ai.lower():
        errors.append("ai.txt does not reference claim registry")

    links = json.loads((ROOT / "api" / "links.json").read_text())
    machine = links.get("machine", [])
    if not any("claim-registry" in m for m in machine):
        errors.append("api/links.json does not reference claim-registry")

    sitemap = (ROOT / "sitemap.xml").read_text()
    if "claim-registry" not in sitemap:
        errors.append("sitemap.xml does not reference claim-registry")

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PUBLIC_CLAIM_TRACEABILITY_OK")


if __name__ == "__main__":
    main()
