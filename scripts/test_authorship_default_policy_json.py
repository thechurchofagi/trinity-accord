#!/usr/bin/env python3
"""Test that API JSON files expose authorship default policy correctly."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
errors = []


def check(condition, msg):
    if not condition:
        errors.append(msg)
        print(f"  FAIL: {msg}")
    else:
        print(f"  PASS: {msg}")


# --- agent-submit-gateway.json ---
submit = json.loads((ROOT / "api" / "agent-submit-gateway.json").read_text())

print("--- agent-submit-gateway.json: authorship_default_policy ---")
adp = submit.get("authorship_default_policy", {})
check(adp, "has authorship_default_policy")
check(adp.get("enabled_by_default") is True, "enabled_by_default == true")
check(adp.get("implementation_location") == "local_builder_only", "implementation_location == local_builder_only")
check(adp.get("gateway_never_receives_private_key") is True, "gateway_never_receives_private_key == true")
check(adp.get("gateway_never_generates_private_key") is True, "gateway_never_generates_private_key == true")
check(adp.get("private_key_must_remain_local") is True, "private_key_must_remain_local == true")
check(adp.get("opt_out_flag") == "--no-authorship-proof", "opt_out_flag == --no-authorship-proof")

benefits = adp.get("benefits", [])
benefits_text = " ".join(benefits)
check("unclaimed" in benefits_text.lower(), "benefits mention unclaimed records")
check("key continuity" in benefits_text.lower() or "key-continuity" in benefits_text.lower(),
      "benefits mention key continuity")
# Check benefits state no authority/verification/reception/attestation/truth/amendment effect
check("authority" in benefits_text.lower() or "verification" in benefits_text.lower(),
      "benefits mention no authority/verification effect")

print("\n--- agent-submit-gateway.json: path-level defaults ---")
pep = submit.get("pure_echo_path", {})
check(pep.get("authorship_proof_default") == "enabled_by_default_local_keypair",
      "pure_echo_path has authorship_proof_default")
check(pep.get("authorship_opt_out_flag") == "--no-authorship-proof",
      "pure_echo_path has authorship_opt_out_flag")

v0v5 = submit.get("v0_v5_archive_submission", {})
check(v0v5.get("authorship_proof_default") == "enabled_by_default_local_keypair",
      "v0_v5_archive_submission has authorship_proof_default")
check(v0v5.get("authorship_opt_out_flag") == "--no-authorship-proof",
      "v0_v5_archive_submission has authorship_opt_out_flag")

vep = submit.get("verification_echo_path", {})
check(vep.get("authorship_proof_default") == "enabled_by_default_local_keypair",
      "verification_echo_path has authorship_proof_default")
check(vep.get("authorship_opt_out_flag") == "--no-authorship-proof",
      "verification_echo_path has authorship_opt_out_flag")

# --- agent-first-contact.json ---
fc = json.loads((ROOT / "api" / "agent-first-contact.json").read_text())

print("\n--- agent-first-contact.json: authorship_default ---")
ad = fc.get("authorship_default", {})
check(ad, "has authorship_default")
check(ad.get("enabled") is True, "enabled == true")
check(ad.get("local_keypair_default") is True, "local_keypair_default == true")
check(ad.get("private_key_never_submitted") is True, "private_key_never_submitted == true")
check(ad.get("gateway_never_receives_private_key") is True, "gateway_never_receives_private_key == true")
check(ad.get("opt_out_flag") == "--no-authorship-proof", "opt_out_flag == --no-authorship-proof")
check("key continuity" in ad.get("boundary", "").lower(), "boundary mentions key continuity")

print(f"\n--- Results: {len(errors)} errors ---")
if errors:
    for e in errors:
        print(f"  ERROR: {e}")
    sys.exit(1)
print("AUTHORSHIP_DEFAULT_POLICY_JSON_OK")
