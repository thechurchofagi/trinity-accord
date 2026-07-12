#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "scripts" / "trinity_record_chain.py"
VALIDATION = ROOT / "apps" / "record_chain_intake_gateway" / "gateway" / "validation.py"

core = CORE.read_text(encoding="utf-8")
validation = VALIDATION.read_text(encoding="utf-8")
required_core = [
    "classification_update requires classification_update_content",
    "classification_update requires valid target_record_id",
    "classification_update requires valid target_record_sha256",
    "classification_update target record",
]
for needle in required_core:
    if needle not in core:
        raise SystemExit(f"missing final classification binding guard: {needle}")
if "INVALID_CLASSIFICATION_TARGET_ID" not in validation:
    raise SystemExit("Gateway must reject noncanonical classification target ids")
print("PASS: classification update target binding is enforced at intake and final verification")
