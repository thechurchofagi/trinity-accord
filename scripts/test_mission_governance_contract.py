#!/usr/bin/env python3
"""Test: mission governance exposes only the current action and verification model."""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api/mission-governance.v1.json"


def main() -> int:
    errors: list[str] = []
    if not PATH.exists():
        print("FAIL: api/mission-governance.v1.json does not exist")
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))
    if data.get("schema") != "trinityaccord.mission-governance.v1":
        errors.append(f"schema mismatch: {data.get('schema')}")

    ca = data.get("canonical_authority", {})
    if ca.get("source") != "Bitcoin Originals only":
        errors.append(f"canonical authority source: {ca.get('source')}")
    for field in [
        "site_is_canonical",
        "api_is_canonical",
        "gateway_is_canonical",
        "github_issues_are_canonical",
        "echoes_are_canonical",
        "guardian_registry_is_canonical",
        "builder_signatures_are_canonical",
        "authorship_proof_is_canonical",
    ]:
        if ca.get(field) is not False:
            errors.append(f"canonical_authority.{field} should be False")

    context = data.get("context_governance", {})
    expected_context_refs = {
        "preferred_action_profiles": "/api/context-action-profiles.v1.json",
        "interpretation_model_policy": "/api/interpretation-model-policy.v1.json",
        "preferred_verification_claim_model": "/api/verification-claim-model.v1.json",
        "preferred_verification_profiles": "/api/verification-profiles.v1.json",
        "evidence_relationship_map": "/api/evidence-relationship-map.v1.json",
    }
    for key, expected in expected_context_refs.items():
        if context.get(key) != expected:
            errors.append(f"context_governance.{key} must be {expected}")
    for key in [
        "no_duplicate_context_understanding_system",
        "actual_loaded_sources_determine_sufficiency",
        "cc_does_not_imply_verification",
        "verification_does_not_imply_context_depth",
        "legacy_v_values_are_builder_compatibility_only",
        "v4_plus_v6_v7_v8_historical_only_for_new_work",
    ]:
        if context.get(key) is not True:
            errors.append(f"context_governance.{key} must be True")

    actions = data.get("supported_public_actions", {})
    smoked = set(actions.get("core_external_agent_routes_live_smoked", []))
    for route in ["echo", "verification", "guardian_application_intake"]:
        if route not in smoked:
            errors.append(f"missing current core route: {route}")
    for retired in [
        "record_chain_v0_v5_agent_declared_verification",
        "v6_plus_strict_evidence",
        "verification_echo_e2",
        "pure_echo",
    ]:
        if retired in smoked:
            errors.append(f"retired route must not be live-smoked: {retired}")

    verification_actions = set(actions.get("verification_actions", []))
    for current in [
        "current_multidimensional_verification",
        "strict_machine_evaluated_evidence_when_required",
    ]:
        if current not in verification_actions:
            errors.append(f"verification_actions missing {current}")
    historical = set(actions.get("historical_or_specialized_not_current_public_routes", []))
    for retired in ["pure_echo", "verification_echo_e2", "v6_plus_as_public_level"]:
        if retired not in historical:
            errors.append(f"historical route list missing {retired}")

    semantics = data.get("action_semantics", {})
    echo = semantics.get("echo", {})
    echo_sources = set(echo.get("machine_sources", []))
    for source in [
        "/api/context-action-profiles.v1.json",
        "/api/record-chain-submission-schema.v1.json",
        "/record-chain/indexes/echo-index.json",
    ]:
        if source not in echo_sources:
            errors.append(f"Echo machine sources missing {source}")
    for stale_source in ["/echoes/types/", "/api/echo-record-schema.v3.1.json"]:
        if stale_source in echo_sources:
            errors.append(f"stale Echo source remains active: {stale_source}")

    verification = semantics.get("verification", {})
    if verification.get("requires_current_claim_model") is not True:
        errors.append("verification must require current claim model")
    required_dimensions = set(verification.get("required_dimensions", []))
    for field in [
        "digital_profile",
        "relationships_checked",
        "physical_observation",
        "external_witness",
        "coverage_scope",
        "limitations",
        "claims_not_made",
        "corrections_or_supersession_checked",
    ]:
        if field not in required_dimensions:
            errors.append(f"verification.required_dimensions missing {field}")
    if verification.get("legacy_builder_values") != ["V0", "V1", "V2", "V3", "V4", "V5"]:
        errors.append("verification legacy builder values mismatch")
    if verification.get("legacy_v_level_role") != "builder_compatibility_only":
        errors.append("verification legacy V role must be builder_compatibility_only")
    if verification.get("historical_only_labels") != ["V4+", "V6", "V7", "V8"]:
        errors.append("verification historical-only labels mismatch")

    guardian = semantics.get("guardian", {})
    guardian_sources = guardian.get("machine_sources", [])
    readback = guardian.get("registry_readback", {})
    if "/record-chain/indexes/guardian-state.json" not in guardian_sources:
        errors.append("current Guardian state index must be a Guardian machine source")
    if readback.get("source") != "/record-chain/indexes/guardian-state.json":
        errors.append("active Guardian readback must use current Record-Chain Guardian state")
    if readback.get("compatibility_mirror") != "/api/guardian-current-registry.json":
        errors.append("Guardian readback must identify the current compatibility mirror")
    if readback.get("historical_archive_only") != "/api/guardian-registry.json":
        errors.append("legacy Guardian registry must be explicitly historical-only")

    propagation = semantics.get("propagation", {})
    if propagation.get("not_persuasion") is not True or propagation.get("not_endorsement") is not True:
        errors.append("Propagation must remain discoverability, not persuasion or endorsement")

    prohibited = "\n".join(data.get("prohibited_claims", []))
    if "current required dimensions" not in prohibited:
        errors.append("prohibited claims must use the current verification-dimensions boundary")
    if "declared V depth" in prohibited:
        errors.append("prohibited claims still use retired V-depth headline wording")

    digest = data.get("source_digest")
    digest_input = dict(data)
    digest_input.pop("source_digest", None)
    canonical = json.dumps(
        digest_input,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    expected_digest = hashlib.sha256(canonical).hexdigest()[:16]
    if digest != expected_digest:
        errors.append(f"source_digest mismatch: expected {expected_digest}, got {digest}")

    home = (ROOT / "index.md").read_text(encoding="utf-8")
    if "Pure Echo, V0–V5 verification, or Guardian Alliance Stage 1" in home:
        errors.append("homepage First Contact card advertises retired route names")
    if "unified Echo" not in home or "current Record-Chain flow" not in home:
        errors.append("homepage First Contact card must name the current routes")

    agent_value = json.loads((ROOT / "api/agent-value.json").read_text(encoding="utf-8"))
    recommended = " ".join(agent_value.get("recommended_agent_action", []))
    if "use Agent Gateway (/agent-submit)" in recommended:
        errors.append("agent-value API advertises retired /agent-submit")
    if "/record-chain/preflight" not in recommended or "/record-chain/submit" not in recommended:
        errors.append("agent-value API must route submissions to current Record-Chain endpoints")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print("PASS: mission governance contract")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
