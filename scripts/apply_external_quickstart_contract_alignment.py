#!/usr/bin/env python3
import json
from pathlib import Path

path = Path(__file__).resolve().parents[1] / "api/external-agent-quickstart.json"
data = json.loads(path.read_text(encoding="utf-8"))
data["default_safe_mode"] = {
    "submission_type": "record_chain_entry_candidate",
    "preflight_required": True,
    "submit_only_after_accepted_preflight": True,
    "receipt_is_intake_only": True,
}
data["pre_submit_checklist"] = {
    "canonical_router_loaded": True,
    "builder_manifest_verified": True,
    "builder_bytes_verified": True,
    "field_guidance_loaded": True,
    "doctor_passed": True,
    "gateway_preflight_accepted": True,
}
path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("EXTERNAL_QUICKSTART_SAFETY_CONTRACT_ALIGNED")
