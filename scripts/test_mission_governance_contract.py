#!/usr/bin/env python3
"""Test: mission governance contract exists and is well-formed."""
import json, sys
from pathlib import Path
errors = []
p = Path("api/mission-governance.v1.json")
if not p.exists():
    print("FAIL: api/mission-governance.v1.json does not exist"); sys.exit(1)
data = json.loads(p.read_text())
if data.get("schema") != "trinityaccord.mission-governance.v1":
    errors.append(f"schema mismatch: {data.get('schema')}")
ca = data.get("canonical_authority", {})
if ca.get("source") != "Bitcoin Originals only":
    errors.append(f"canonical authority source: {ca.get('source')}")
for field in ["site_is_canonical","api_is_canonical","gateway_is_canonical","github_issues_are_canonical","echoes_are_canonical","guardian_registry_is_canonical","builder_signatures_are_canonical","authorship_proof_is_canonical"]:
    if ca.get(field) is not False:
        errors.append(f"canonical_authority.{field} should be False")
cg = data.get("context_governance", {})
for ref in ["context_depth_levels","context_readiness_levels","crl_to_context_depth_mapping","verification_levels","resonance_willingness_scale"]:
    if ref not in cg: errors.append(f"context_governance missing: {ref}")
if cg.get("no_duplicate_context_understanding_system") is not True:
    errors.append("no_duplicate_context_understanding_system must be True")
smoked = data.get("supported_public_actions",{}).get("core_external_agent_routes_live_smoked",[])
for route in ["echo","record_chain_v0_v5_agent_declared_verification","guardian_application_intake"]:
    if route not in smoked: errors.append(f"missing current core route: {route}")
for retired_route in ["pure_echo","v0_v5_agent_declared_archive","guardian_application_stage_1"]:
    if retired_route in smoked: errors.append(f"retired Gateway v1 route must not be live-smoked as current: {retired_route}")
semantics = data.get("action_semantics", {})
echo_sources = semantics.get("echo", {}).get("machine_sources", [])
if "/record-chain/indexes/echo-index.json" not in echo_sources:
    errors.append("current Record-Chain Echo index must be an Echo machine source")
if "/api/echo-types.json" in echo_sources:
    errors.append("deprecated Echo taxonomy must not be a current Echo machine source")
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
home = Path("index.md").read_text(encoding="utf-8")
if "Pure Echo, V0–V5 verification, or Guardian Alliance Stage 1" in home:
    errors.append("homepage First Contact card advertises retired route names")
if "unified Echo" not in home or "current Record-Chain flow" not in home:
    errors.append("homepage First Contact card must name the current routes")
agent_value = json.loads(Path("api/agent-value.json").read_text(encoding="utf-8"))
recommended = " ".join(agent_value.get("recommended_agent_action", []))
if "use Agent Gateway (/agent-submit)" in recommended:
    errors.append("agent-value API advertises retired /agent-submit")
if "/record-chain/preflight" not in recommended or "/record-chain/submit" not in recommended:
    errors.append("agent-value API must route submissions to current Record-Chain endpoints")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
print("PASS: mission governance contract")
