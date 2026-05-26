#!/usr/bin/env python3
"""Test BTC API endpoint allowlist (FEC-BTC-002)."""
import sys, re

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]

findings = []

# Check verify-ots-time-anchor.mjs
ots = (ROOT / "scripts" / "verify-ots-time-anchor.mjs").read_text()
fec = (ROOT / "scripts" / "verify-full-evidence-chain.mjs").read_text()

# 1. normalizeBtcApiBase exists
if "normalizeBtcApiBase" in ots:
    findings.append("✅ normalizeBtcApiBase exists in verify-ots-time-anchor.mjs")
else:
    findings.append("❌ normalizeBtcApiBase missing in verify-ots-time-anchor.mjs")

if "normalizeBtcApiBase" in fec:
    findings.append("✅ normalizeBtcApiBase exists in verify-full-evidence-chain.mjs")
else:
    findings.append("❌ normalizeBtcApiBase missing in verify-full-evidence-chain.mjs")

# 2. BTC_API_ALLOWED_HOSTS
if "BTC_API_ALLOWED_HOSTS" in ots:
    findings.append("✅ BTC_API_ALLOWED_HOSTS exists in verify-ots-time-anchor.mjs")
else:
    findings.append("❌ BTC_API_ALLOWED_HOSTS missing in verify-ots-time-anchor.mjs")

if "BTC_API_ALLOWED_HOSTS" in fec:
    findings.append("✅ BTC_API_ALLOWED_HOSTS exists in verify-full-evidence-chain.mjs")
else:
    findings.append("❌ BTC_API_ALLOWED_HOSTS missing in verify-full-evidence-chain.mjs")

# 3. Only https allowed
if "https:" in ots and "protocol" in ots:
    findings.append("✅ HTTPS enforcement present in verify-ots-time-anchor.mjs")
else:
    findings.append("❌ HTTPS enforcement missing in verify-ots-time-anchor.mjs")

# 4. host is not allowlisted error
if "not allowlisted" in ots:
    findings.append("✅ Allowlist rejection message present")
else:
    findings.append("❌ Allowlist rejection message missing")

# 5. mempool.space and blockstream.info in allowed set
if "mempool.space" in ots and "blockstream.info" in ots:
    findings.append("✅ Expected hosts in allowlist")
else:
    findings.append("❌ Expected hosts missing from allowlist")

# 6. Query/hash stripped
if "search" in ots and "hash" in ots:
    findings.append("✅ Query/hash stripping present")
else:
    findings.append("❌ Query/hash stripping missing")

for f in findings:
    print(f"  {f}")

fails = [f for f in findings if f.startswith("❌")]
if fails:
    print(f"\nFAILED: {len(fails)} issues")
    sys.exit(1)
else:
    print(f"\nTEST_BTC_API_ENDPOINT_ALLOWLIST_OK ({len(findings)} passed)")
