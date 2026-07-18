#!/usr/bin/env python3
from pathlib import Path
p = Path(__file__).resolve().parents[1] / "external-agent-quickstart.md"
t = p.read_text(encoding="utf-8")
t = t.replace("Run `node record-chain-builder.mjs print-oath --record-type echo|verification|guardian_application` for formal record types.", "Formal oath output applies to echo, verification, guardian_application, guardian_retirement, propagation, correction, and classification_update.")
t = t.replace("Build Echo, V0–V5 Verification, or Guardian Application with exact `--readback`, explicit context, and authorship proof.", "The current Builder covers all eight record types; the seven formal types include oath readback, context/provenance fields, and authorship proof, while context_insufficient_notice is the non-formal exception.")
p.write_text(t, encoding="utf-8")
print("QUICKSTART_SCOPE_FIXED")
