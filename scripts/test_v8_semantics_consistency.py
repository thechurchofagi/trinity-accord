#!/usr/bin/env python3
"""VR-001: V8 semantics consistency across component levels, protocol profiles, and claim-gate rules."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

component = json.loads((ROOT / "api" / "component-verification-levels.json").read_text(encoding="utf-8"))
profiles = json.loads((ROOT / "api" / "protocol-verification-profiles.json").read_text(encoding="utf-8"))
rules = json.loads((ROOT / "api" / "claim-gate-rules.json").read_text(encoding="utf-8"))

errors = []


def find_profile(level):
    for p in profiles.get("profiles", []):
        if p.get("level") == level:
            return p
    return None


def find_component_protocol(level):
    for p in component.get("protocol_levels", []):
        if p.get("level") == level:
            return p
    return None


def find_rule(level):
    for r in rules.get("protocol_level_rules", []):
        if r.get("level") == level:
            return r
    return None


v8_profile = find_profile("V8")
v8_component = find_component_protocol("V8")
v8_rule = find_rule("V8")

if not v8_profile:
    errors.append("protocol-verification-profiles.json missing V8 profile")
if not v8_component:
    errors.append("component-verification-levels.json missing V8 protocol level")
if not v8_rule:
    errors.append("claim-gate-rules.json missing V8 rule")

if v8_profile and v8_rule:
    profile_any = v8_profile.get("minimum_component_requirements_any", [])
    rule_any = v8_rule.get("requires_one_of", [])

    profile_mentions_t8 = "T8" in json.dumps(profile_any)
    rule_mentions_t8 = "T8" in json.dumps(rule_any)

    if profile_mentions_t8 != rule_mentions_t8:
        errors.append(
            "V8 T8 path mismatch: profile and claim-gate-rules disagree on whether T8 can be a V8 path"
        )

    profile_mentions_p7 = "P7" in json.dumps(profile_any) or "P7" in json.dumps(v8_profile.get("minimum_component_requirements", {}))
    rule_mentions_p7 = "P7" in json.dumps(rule_any)

    if profile_mentions_p7 != rule_mentions_p7:
        errors.append(
            "V8 P7 path mismatch: profile and claim-gate-rules disagree on physical P7 path"
        )

if v8_component:
    name = v8_component.get("name", "").lower()
    data_sources = json.dumps(v8_component.get("data_sources", []), ensure_ascii=False).lower()
    method = v8_component.get("method", "").lower()

    # For方案 A: V8 includes celestial path.
    if "celestial" not in name and "celestial" not in data_sources and "celestial" not in method:
        errors.append("component-verification-levels V8 does not mention celestial path while rules/profile allow T8")

if errors:
    print("V8_SEMANTICS_CONSISTENCY_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("V8_SEMANTICS_CONSISTENCY_OK")
