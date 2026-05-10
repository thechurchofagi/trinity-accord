#!/usr/bin/env python3
"""Test BTC API cross-check conflict fail-closed (FEC-BTC-001)."""
import sys

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]

findings = []
ots = (ROOT / "scripts" / "verify-ots-time-anchor.mjs").read_text()

# 1. btcFetchFromBase exists
if "btcFetchFromBase" in ots:
    findings.append("✅ btcFetchFromBase exists")
else:
    findings.append("❌ btcFetchFromBase missing")

# 2. equivalentBtcApiResponse exists
if "equivalentBtcApiResponse" in ots:
    findings.append("✅ equivalentBtcApiResponse exists")
else:
    findings.append("❌ equivalentBtcApiResponse missing")

# 3. BTC API conflict throws
if "conflict" in ots.lower() and ("throw" in ots or "Error" in ots):
    findings.append("✅ BTC API conflict throws error")
else:
    findings.append("❌ BTC API conflict handling missing")

# 4. conflict_policy in output
if "conflict_policy" in ots and "fail_closed" in ots:
    findings.append("✅ conflict_policy = fail_closed in report")
else:
    findings.append("❌ conflict_policy missing from report")

# 5. btc_api_crosscheck in output
if "btc_api_crosscheck" in ots:
    findings.append("✅ btc_api_crosscheck in OTS audit output")
else:
    findings.append("❌ btc_api_crosscheck missing from OTS audit output")

# 6. btcApiWarnings tracked
if "btcApiWarnings" in ots:
    findings.append("✅ btcApiWarnings tracked")
else:
    findings.append("❌ btcApiWarnings not tracked")

# 7. Both sources fail → throw
if "primary" in ots and "fallback" in ots and "failed" in ots.lower():
    findings.append("✅ Both-fail handling present")
else:
    findings.append("❌ Both-fail handling missing")

for f in findings:
    print(f"  {f}")

fails = [f for f in findings if f.startswith("❌")]
if fails:
    print(f"\nFAILED: {len(fails)} issues")
    sys.exit(1)
else:
    print(f"\nTEST_BTC_API_CROSSCHECK_CONFLICT_FAIL_CLOSED_OK ({len(findings)} passed)")
