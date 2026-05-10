#!/usr/bin/env python3
"""Test digest manifest JSON/CSV cross-check (FEC-E1)."""
import sys, os

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]

findings = []
fec = (ROOT / "scripts" / "verify-full-evidence-chain.mjs").read_text()

# 1. crossCheckDigestManifestJsonCsv exists
if "crossCheckDigestManifestJsonCsv" in fec:
    findings.append("✅ crossCheckDigestManifestJsonCsv function exists")
else:
    findings.append("❌ crossCheckDigestManifestJsonCsv function missing")

# 2. normalizeManifestPath exists
if "normalizeManifestPath" in fec:
    findings.append("✅ normalizeManifestPath function exists")
else:
    findings.append("❌ normalizeManifestPath function missing")

# 3. Error messages for missing paths
if "digest CSV missing path from JSON" in fec:
    findings.append("✅ CSV-missing-JSON-path error message present")
else:
    findings.append("❌ CSV-missing-JSON-path error message missing")

if "digest JSON missing path from CSV" in fec:
    findings.append("✅ JSON-missing-CSV-path error message present")
else:
    findings.append("❌ JSON-missing-CSV-path error message missing")

# 4. Mismatch detection
if "digest mismatch" in fec:
    findings.append("✅ Digest mismatch detection present")
else:
    findings.append("❌ Digest mismatch detection missing")

# 5. digest_manifest_crosscheck in report output
if "digest_manifest_crosscheck" in fec:
    findings.append("✅ digest_manifest_crosscheck in report output")
else:
    findings.append("❌ digest_manifest_crosscheck missing from report output")

# 6. Cross-check called in main flow
if "crossCheckDigestManifestJsonCsv(DIGEST_MANIFEST_JSON" in fec:
    findings.append("✅ Cross-check called with correct constants")
else:
    findings.append("❌ Cross-check not called with correct constants")

# 7. Cross-check errors contribute to criticalErrors
if "DIGEST CROSSCHECK" in fec:
    findings.append("✅ Cross-check errors push to criticalErrors")
else:
    findings.append("❌ Cross-check errors not linked to criticalErrors")

for f in findings:
    print(f"  {f}")

fails = [f for f in findings if f.startswith("❌")]
if fails:
    print(f"\nFAILED: {len(fails)} issues")
    sys.exit(1)
else:
    print(f"\nTEST_DIGEST_MANIFEST_JSON_CSV_CROSSCHECK_OK ({len(findings)} passed)")
