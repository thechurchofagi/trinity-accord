#!/usr/bin/env python3
"""Final red-team regression: local token_index fallback must not be reported as ETH tokenURI verification."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "scripts" / "verify-full-evidence-chain.mjs").read_text(encoding="utf-8")

errors = []

for marker in [
    "ethAuditAvailable",
    "eth_tokenuri_status",
    "not_checked",
    "ETH tokenURI 175/175 not checked",
    "onchain_tokenuri_175_pass",
]:
    if marker not in text:
        errors.append(f"missing ETH audit boundary marker: {marker}")

if re.search(r"onchain_tokenuri_175_pass\s*:\s*true", text):
    errors.append("report must not hard-code onchain_tokenuri_175_pass: true")

danger_patterns = [
    r"onchain\w*175\w*=\s*true[^;\n]*token",
    r"ETH tokenURI.*175/175.*verified",
    r"ETH tokenURI.*175/175.*pass",
]

for pat in danger_patterns:
    for m in re.finditer(pat, text, re.IGNORECASE | re.DOTALL):
        window = text[max(0, m.start() - 400):m.end() + 400]
        if "ethAuditAvailable" not in window and "ethTokenUriStatus" not in window and "claims_not_made" not in window:
            errors.append(f"unguarded ETH tokenURI overclaim pattern: {pat}")
            break

if errors:
    print("FULL_EVIDENCE_CHAIN_ETH_AUDIT_REQUIRED_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("FULL_EVIDENCE_CHAIN_ETH_AUDIT_REQUIRED_OK")
