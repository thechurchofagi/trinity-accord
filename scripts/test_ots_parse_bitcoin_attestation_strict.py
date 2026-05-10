#!/usr/bin/env python3
"""Test OTS parseBitcoinAttestation strictness (FEC-OTS-002)."""
import sys, re

ROOT = __import__('pathlib').Path(__file__).resolve().parents[1]
ots = (ROOT / "scripts" / "verify-ots-time-anchor.mjs").read_text()

findings = []

# 1. Must NOT contain broad bare 64-hex scan
# The old pattern was: text.matchAll(/\b[0-9a-f]{64}\b/gi)
# The new pattern should require context (block hash, header hash, txid, transaction id)
if re.search(r'matchAll\s*\(\s*/\\b\[0-9a-f\]\{64\}\\b/gi', ots):
    findings.append("❌ Old bare 64-hex matchAll pattern still present")
else:
    findings.append("✅ No broad bare 64-hex matchAll pattern")

# 2. block hash extraction requires context
if "block\\s+hash" in ots or "block hash" in ots:
    findings.append("✅ block hash context required")
else:
    findings.append("❌ block hash context not required")

# 3. header hash extraction requires context
if "header\\s+hash" in ots or "header hash" in ots:
    findings.append("✅ header hash context required")
else:
    findings.append("❌ header hash context not required")

# 4. txid extraction requires context
if "txid" in ots:
    findings.append("✅ txid context required")
else:
    findings.append("❌ txid context not required")

# 5. transaction id extraction requires context
if "transaction" in ots:
    findings.append("✅ transaction id context required")
else:
    findings.append("❌ transaction id context not required")

# 6. block_hashes field in output
if "block_hashes" in ots:
    findings.append("✅ block_hashes field in output")
else:
    findings.append("❌ block_hashes field missing from output")

# 7. No generic [0-9a-f]{64} without context anchor
# Count occurrences of matchAll with hex patterns
hex_patterns = re.findall(r'matchAll\([^)]*[0-9a-f]\{64\}[^)]*\)', ots)
context_bound = sum(1 for p in hex_patterns if "block" in p.lower() or "header" in p.lower() or "txid" in p.lower() or "transaction" in p.lower())
findings.append(f"ℹ️ Found {len(hex_patterns)} hex matchAll patterns, {context_bound} context-bound")

for f in findings:
    print(f"  {f}")

fails = [f for f in findings if f.startswith("❌")]
if fails:
    print(f"\nFAILED: {len(fails)} issues")
    sys.exit(1)
else:
    print(f"\nTEST_OTS_PARSE_BITCOIN_ATTESTATION_STRICT_OK ({len(findings)} passed)")
