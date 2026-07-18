#!/usr/bin/env python3
from pathlib import Path

PATH = Path(__file__).resolve().parents[1] / "llms-full.txt"
text = PATH.read_text(encoding="utf-8")

def swap(old, new):
    global text
    if old not in text: raise RuntimeError(f"missing llms-full target: {old[:60]}")
    text = text.replace(old, new, 1)

swap("# Agent Entry Protocol v3", "# Current Full Machine Context")
swap("- Claim Gate required for technical verification claims.", "- Current verification claims use multidimensional profiles and exact performed actions; strict machine-evaluated evidence additionally uses fresh Evidence Input and Claim Gate.")
swap("- Legacy V0–V8 and CC/CRL remain current Builder/archive compatibility metadata; do not delete them from current submissions.", "- Builder values V0–V5 and CC/CRL remain compatibility metadata. V4+, V6, V7, and V8 are historical-only labels for new public submissions.")
swap("- V6–V8 strict technical claims: use Evidence Input → Claim Gate → report builder → validator before the Record-Chain submission.", "- Strict machine-evaluated evidence: use fresh Evidence Input → Claim Gate → report builder → validator, while public verification remains V0–V5 compatibility metadata plus current multidimensional fields.")
swap("Required first path for AI agents:\n\n1. /agent-brief", "Required first path for AI agents:\n\n1. /api/agent-first-contact.json\n2. /agent-first-contact/\n3. /api/agent-start.v2.json\n4. /api/agent-required-reading.json\n5. /api/record-chain-builder-bundles.v1.json\n6. /downloads/record-chain-builder.mjs\n7. /downloads/record-chain-agent-field-guidance.v1.json\n8. /api/record-chain-intake-gateway.v1.json\n9. /api/record-chain-status.json\n\nTask-specific context follows the canonical router. Historical routes do not override this sequence.\n\nLegacy narrative sequence (historical context only):\n\n1. /agent-brief")
swap("Preserve the V0-V8 verification system.", "Preserve V0–V8 only in historical records. New public Builder submissions accept V0–V5 compatibility metadata and current multidimensional verification fields.")
swap("Use /api/echo-record-schema.v3.1.json together with /api/record-chain-submission-schema.v1.json for current Echo records.", "Use the unified Record-Chain submission schema and current Builder for Echo records. Legacy Echo schemas are historical compatibility material.")
PATH.write_text(text, encoding="utf-8")
print("LLMS_FULL_DRIFT_FIXED")
