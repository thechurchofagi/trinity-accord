#!/usr/bin/env python3
"""VR-010: Cross-file verification rule consistency matrix.

Detects divergence between:
  - component-verification-levels.json
  - protocol-verification-profiles.json
  - claim-gate-rules.json
  - evidence-input-schema.v1.json
  - scripts/claim_gate.py
"""
import json
from pathlib import Path
import sys
import re

ROOT = Path(__file__).resolve().parents[1]

component = json.loads((ROOT / "api" / "component-verification-levels.json").read_text(encoding="utf-8"))
profiles = json.loads((ROOT / "api" / "protocol-verification-profiles.json").read_text(encoding="utf-8"))
rules = json.loads((ROOT / "api" / "claim-gate-rules.json").read_text(encoding="utf-8"))
schema = json.loads((ROOT / "api" / "evidence-input-schema.v1.json").read_text(encoding="utf-8"))
claim_gate = (ROOT / "scripts" / "claim_gate.py").read_text(encoding="utf-8")

errors = []


def profile(level):
    return next((p for p in profiles.get("profiles", []) if p.get("level") == level), None)


def rule(level):
    return next((r for r in rules.get("protocol_level_rules", []) if r.get("level") == level), None)


def component_protocol(level):
    return next((p for p in component.get("protocol_levels", []) if p.get("level") == level), None)


# 1. Every V-level in profiles has a rule and component description.
for p in profiles.get("profiles", []):
    lvl = p.get("level")
    if not rule(lvl):
        errors.append(f"{lvl}: missing claim-gate-rules protocol rule")
    if not component_protocol(lvl):
        errors.append(f"{lvl}: missing component-verification-levels protocol description")

# 2. Every V-level in rules has a profile.
for r in rules.get("protocol_level_rules", []):
    lvl = r.get("level")
    if not profile(lvl):
        errors.append(f"{lvl}: rule exists but protocol profile missing")

# 3. Claim Gate execution status must reflect implementation.
if rules.get("execution_status") == "documentation_only" and "def evaluate" in claim_gate:
    errors.append("claim-gate-rules.json says documentation_only but scripts/claim_gate.py implements evaluate()")

# 4. V8 T8/P7 path consistency.
v8_p = profile("V8") or {}
v8_r = rule("V8") or {}
v8_c = component_protocol("V8") or {}

profile_text = json.dumps(v8_p)
rule_text = json.dumps(v8_r)
component_text = json.dumps(v8_c).lower()

profile_t8 = "T8" in profile_text
rule_t8 = "T8" in rule_text

if profile_t8 != rule_t8:
    errors.append("V8 T8 path mismatch between profile and claim-gate-rules")

if rule_t8 and "celestial" not in component_text:
    errors.append("V8 rule allows T8 but component V8 description does not mention celestial")

# 5. V3 hash artifact mapping exists.
v3 = profile("V3") or {}
mapping = v3.get("hash_artifact_class_to_component_level", {})
for key in [
    "canonical_mirror",
    "repository_snapshot",
    "chronicle_recovery_package",
    "physical_evidence_package",
]:
    if key not in mapping:
        errors.append(f"V3 missing hash artifact class mapping: {key}")

# 6. Schema should mention major high-level evidence fields.
schema_text = json.dumps(schema)
for field in [
    "package_hash",
    "verifier_identity_or_role",
    "witnesses",
    "method_class",
]:
    if field not in schema_text:
        errors.append(f"evidence schema missing high-level field: {field}")

# 7. CI should reference this test.
workflow_text = ""
wf = ROOT / ".github" / "workflows" / "repository-integrity.yml"
if wf.exists():
    workflow_text = wf.read_text(encoding="utf-8")
    if "test_verification_rule_consistency_matrix.py" not in workflow_text:
        errors.append("repository-integrity.yml does not run test_verification_rule_consistency_matrix.py")

if errors:
    print("VERIFICATION_RULE_CONSISTENCY_MATRIX_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("VERIFICATION_RULE_CONSISTENCY_MATRIX_OK")
