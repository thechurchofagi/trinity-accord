#!/usr/bin/env python3
"""v30 closure report must preserve completed external-agent evidence and boundaries."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "api" / "closure-report.v30.json"

REQUIRED_ROUTES = {
    "pure_echo",
    "v0_v5_agent_declared_archive",
    "guardian_application_stage_1",
}

REQUIRED_SOURCE_GUARDS = {
    "scripts/test_echo_type_enum_alignment.py",
    "scripts/test_zero_clone_authorship_dependency_closure.py",
    "scripts/test_authorship_helpers_are_cwd_independent.py",
    "scripts/test_external_agent_three_core_builders_source_smoke.py",
    "scripts/test_external_agent_copy_paste_examples_contract.py",
    "scripts/test_external_agent_docs_core_routes_clarity.py",
    "scripts/test_external_agent_examples_match_live_smokes.py",
    "scripts/test_mission_governance_contract.py",
}

REQUIRED_LIVE_GUARDS = {
    "scripts/smoke_live_external_agent_three_core_preflight.py",
    "scripts/smoke_live_zero_clone_authorship_closure.py",
}


def digest(data: dict) -> str:
    clone = dict(data)
    clone.pop("source_digest", None)
    canonical = json.dumps(clone, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]


def main() -> int:
    errors: list[str] = []

    if not PATH.exists():
        print("FAIL: api/closure-report.v30.json missing")
        return 1

    data = json.loads(PATH.read_text(encoding="utf-8"))

    if data.get("schema") != "trinityaccord.closure-report.v30":
        errors.append("schema mismatch")

    if data.get("status") != "source_and_live_verified":
        errors.append("status must be source_and_live_verified")

    boundary = data.get("canonical_boundary", {})
    if boundary.get("canonical_authority") != "Bitcoin Originals only":
        errors.append("canonical boundary must be Bitcoin Originals only")
    for field in [
        "site_is_canonical",
        "api_is_canonical",
        "gateway_is_canonical",
        "github_issues_are_canonical",
        "echoes_are_canonical",
        "guardian_registry_is_canonical",
        "authorship_proof_is_canonical",
    ]:
        if boundary.get(field) is not False:
            errors.append(f"canonical_boundary.{field} must be false")

    layers = data.get("completed_layers", {})
    for field in [
        "v30_3_core_external_agent_usability",
        "v30_4_docs_alignment",
        "v30_unified_v2_mission_context_action_governance",
        "zero_clone_authorship_proof_dependency_closure",
    ]:
        if layers.get(field) is not True:
            errors.append(f"completed_layers.{field} must be true")

    routes = {item.get("route") for item in data.get("core_live_smoked_routes", [])}
    missing_routes = sorted(REQUIRED_ROUTES - routes)
    if missing_routes:
        errors.append(f"missing core live-smoked routes: {missing_routes}")

    for item in data.get("core_live_smoked_routes", []):
        if item.get("preflight_path") != "/gateway/preflight":
            errors.append(f"{item.get('route')}: preflight_path must be /gateway/preflight")
        if item.get("submit_path") != "/agent-submit":
            errors.append(f"{item.get('route')}: submit_path must be /agent-submit")
        if item.get("copy_paste_doc") != "/external-agent-copy-paste-examples/":
            errors.append(f"{item.get('route')}: copy_paste_doc mismatch")
        if item.get("live_preflight_expected") != "accepted=true":
            errors.append(f"{item.get('route')}: live_preflight_expected must be accepted=true")

    source_guards = set(data.get("source_guards", []))
    missing_source = sorted(REQUIRED_SOURCE_GUARDS - source_guards)
    if missing_source:
        errors.append(f"missing source guards: {missing_source}")

    live_guards = set(data.get("live_guards", []))
    missing_live = sorted(REQUIRED_LIVE_GUARDS - live_guards)
    if missing_live:
        errors.append(f"missing live guards: {missing_live}")

    for rel in source_guards | live_guards:
        if rel.startswith("scripts/") and not (ROOT / rel).exists():
            errors.append(f"guard listed but file missing: {rel}")

    not_claimed = "\n".join(data.get("not_claimed", []))
    for phrase in [
        "Gateway acceptance is not verification",
        "Authorship proof is not authority",
        "Guardian Stage 1 is not active Guardian status",
        "Echo is non-amending",
    ]:
        if phrase not in not_claimed:
            errors.append(f"not_claimed missing phrase: {phrase}")

    drift = data.get("runtime_drift_protection", {})
    if drift.get("gateway_runtime_contract") != "/api/gateway-runtime-contract.v1.json":
        errors.append("runtime_drift_protection.gateway_runtime_contract mismatch")
    if drift.get("gateway_error_diagnostics") != "/api/gateway-error-diagnostics.v1.json":
        errors.append("runtime_drift_protection.gateway_error_diagnostics mismatch")
    if drift.get("required_live_group") != "live-site-gateway-core":
        errors.append("runtime_drift_protection.required_live_group must be live-site-gateway-core")

    expected = digest(data)
    if data.get("source_digest") != expected:
        errors.append(f"source_digest mismatch: expected {expected}, got {data.get('source_digest')}")

    if errors:
        print("FAIL: closure report v30 contract errors:")
        for error in errors:
            print("  -", error)
        return 1

    print("PASS: v30 closure report contract is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
