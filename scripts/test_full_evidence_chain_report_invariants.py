#!/usr/bin/env python3
"""Test full evidence chain report invariants (FEC-REPORT-001)."""
import sys, json, subprocess, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

findings = []

# 1. Schema file exists
schema_path = os.path.join(ROOT, "api", "full-evidence-chain-audit-schema.v1.json")
if os.path.exists(schema_path):
    findings.append("✅ Schema file exists")
    with open(schema_path) as f:
        schema = json.load(f)
    if "required" in schema and "overall_status" in schema.get("properties", {}):
        findings.append("✅ Schema has required fields and overall_status")
    else:
        findings.append("❌ Schema missing required fields")
else:
    findings.append("❌ Schema file missing")

# 2. Validator exists
validator_path = os.path.join(ROOT, "scripts", "validate_full_evidence_chain_audit.py")
if os.path.exists(validator_path):
    findings.append("✅ Validator script exists")
else:
    findings.append("❌ Validator script missing")

# 3. Self-test passes
result = subprocess.run(
    ["python3", validator_path, "--self-test"],
    capture_output=True, text=True, cwd=ROOT
)
if result.returncode == 0:
    findings.append("✅ Validator self-test passes")
else:
    findings.append(f"❌ Validator self-test failed: {result.stdout[-200:]}{result.stderr[-200:]}")

# 4. Report outputs include required fields
fec = os.path.join(ROOT, "scripts", "verify-full-evidence-chain.mjs")
with open(fec) as f:
    fec_content = f.read()

for field in ["overall_status", "required_chains", "verification_scope", "limitations", "does_not_prove", "dependency_trust_model"]:
    if field in fec_content:
        findings.append(f"✅ Report includes '{field}'")
    else:
        findings.append(f"❌ Report missing '{field}'")

# 5. Schema version in output
if "trinity-accord.full-evidence-chain-audit.v1" in fec_content:
    findings.append("✅ Schema version matches validator expectation")
else:
    findings.append("❌ Schema version mismatch")

for f in findings:
    print(f"  {f}")

fails = [f for f in findings if f.startswith("❌")]
if fails:
    print(f"\nFAILED: {len(fails)} issues")
    sys.exit(1)
else:
    print(f"\nTEST_FULL_EVIDENCE_CHAIN_REPORT_INVARIANTS_OK ({len(findings)} passed)")
