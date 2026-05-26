#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "claim_gate_rules": "/api/claim-gate-rules.json",
    "evidence_input_schema": "/api/evidence-input-schema.v1.json",
    "claim_gate_output_schema": "/api/claim-gate-output-schema.v1.json",
    "report_builder_policy": "/api/report-builder-policy.json",
    "agent_submission_guide": "/api/agent-submission-guide.json",
    "verification_report_schema_v2": "/api/verification-report-schema.v2.json",
    "generated_by_schema": "/api/generated-by-schema.v1.json",
}

def main():
    data = json.loads((ROOT / ".well-known/trinity-accord.json").read_text(encoding="utf-8"))
    gate = data.get("submission_gate")
    assert isinstance(gate, dict), ".well-known missing submission_gate"

    for key, expected in REQUIRED.items():
        assert gate.get(key) == expected, f"submission_gate.{key} must be {expected}"

    # Ensure starting from .well-known alone gives enough routing info.
    api = data.get("api", {})
    assert api.get("authority") == "/api/authority.json"
    assert api.get("verification_levels") == "/api/verification-levels.json"
    assert api.get("echo_record_schema_v3") == "/api/echo-record-schema.v3.json"

if __name__ == "__main__":
    main()
