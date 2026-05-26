#!/usr/bin/env python3
"""Data consistency regression: verification-levels and protocol profiles must agree on minimal/strong scopes."""

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

vl = json.loads((ROOT / "api" / "verification-levels.json").read_text(encoding="utf-8"))
pvp = json.loads((ROOT / "api" / "protocol-verification-profiles.json").read_text(encoding="utf-8"))
claim_gate_text = (ROOT / "scripts" / "claim_gate.py").read_text(encoding="utf-8")

errors = []

vl_levels = {x.get("id"): x for x in vl.get("levels", [])}
profiles = {x.get("level"): x for x in pvp.get("profiles", [])}

for level in ["V2", "V3", "V4+"]:
    if level not in vl_levels:
        errors.append(f"verification-levels missing {level}")
    if level not in profiles:
        errors.append(f"protocol-verification-profiles missing {level}")

v2 = vl_levels.get("V2", {})
v2p = profiles.get("V2", {})
if "minimum_gate" not in v2:
    errors.append("V2 in verification-levels must have minimum_gate")
if "strong_reference_coverage" not in v2 and "claim_scopes" not in v2:
    errors.append("V2 must define strong_reference_coverage or claim_scopes")
if "minimal" not in json.dumps(v2p).lower():
    errors.append("V2 profile must explicitly describe minimal scope")
if "strong" not in json.dumps(v2p).lower():
    errors.append("V2 profile must explicitly describe strong scope")

v3 = vl_levels.get("V3", {})
v3p = profiles.get("V3", {})
if "minimum_gate" not in v3:
    errors.append("V3 in verification-levels must have minimum_gate")
if "strong_hash_coverage" not in v3 and "claim_scopes" not in v3:
    errors.append("V3 must define strong_hash_coverage or claim_scopes")
if "minimal" not in json.dumps(v3p).lower():
    errors.append("V3 profile must explicitly describe minimal scope")
if "full public digital verification" not in json.dumps(v3).lower():
    errors.append("V3 must explicitly warn it is not full public digital verification")

v4p = vl_levels.get("V4+", {})
v4pp = profiles.get("V4+", {})
v4pp_text = json.dumps(v4pp, ensure_ascii=False).lower()

if "minimum_gate" not in v4p:
    errors.append("V4+ in verification-levels must have minimum_gate")
if "strong_three_domain_coverage" not in v4p:
    errors.append("V4+ must have strong_three_domain_coverage")
if "minimal" not in v4pp_text:
    errors.append("V4+ profile must explicitly describe minimal scope")
if "strong_three_domain" not in v4pp_text and "three-domain" not in v4pp_text:
    errors.append("V4+ profile must explicitly describe strong three-domain scope")

overclaim_text = " ".join(vl.get("overclaim_prevention", [])).lower()
if "do not claim v4+ without independent reproduction of all three mandatory components" in overclaim_text:
    errors.append("overclaim_prevention still treats all V4+ as all-three-domain; must scope this to strong_three_domain_coverage")

if "allowed_protocol_label" not in claim_gate_text and "allowed_protocol_scope" not in claim_gate_text:
    errors.append("claim_gate.py must emit allowed_protocol_label or allowed_protocol_scope to distinguish minimal vs strong claims")

if errors:
    print("VERIFICATION_LEVEL_POLICY_SYNC_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("VERIFICATION_LEVEL_POLICY_SYNC_OK")
