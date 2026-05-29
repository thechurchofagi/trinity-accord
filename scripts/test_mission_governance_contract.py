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
for route in ["pure_echo","v0_v5_agent_declared_archive","guardian_application_stage_1"]:
    if route not in smoked: errors.append(f"missing core route: {route}")
if errors:
    for e in errors: print(f"FAIL: {e}")
    sys.exit(1)
print("PASS: mission governance contract")
