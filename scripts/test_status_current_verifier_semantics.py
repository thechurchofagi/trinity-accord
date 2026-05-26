#!/usr/bin/env python3
"""Data consistency regression: status.md must not present old full evidence run as current after verifier hardening."""

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
text = (ROOT / "status.md").read_text(encoding="utf-8")

errors = []

mentions_old_run = "Verify Full Evidence Chain #8" in text or "Commit: `3741e78`" in text
claims_current_pass = re.search(r"\*\*Status:\s*✅ PASS\*\*", text) is not None
has_boundary = "Current semantic boundary" in text or "Historical status" in text
mentions_hardened = all(
    phrase in text
    for phrase in [
        "OTS",
        "ETH tokenURI",
        "Arweave",
    ]
)

if mentions_old_run and claims_current_pass and not has_boundary:
    errors.append("status.md presents old full evidence run as current PASS without historical/current semantics boundary")

if mentions_old_run and not mentions_hardened:
    errors.append("status.md old run must mention hardened OTS / ETH tokenURI / Arweave verifier semantics")

if "needs fresh current-semantics run" not in text and mentions_old_run:
    errors.append("status.md should mark old full evidence fields as needing fresh current-semantics run unless updated to a new run")

if errors:
    print("STATUS_CURRENT_VERIFIER_SEMANTICS_FAIL")
    for e in errors:
        print("-", e)
    sys.exit(1)

print("STATUS_CURRENT_VERIFIER_SEMANTICS_OK")
