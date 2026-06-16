#!/usr/bin/env python3
"""Smoke tests for agent submit field guidance."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUIDANCE = ROOT / "api" / "record-chain-agent-field-guidance.v1.json"
CLI = ROOT / "downloads" / "record-chain-agent-submit-guide.mjs"


def run_cli(*args: str) -> str:
    return subprocess.check_output(
        ["node", str(CLI), *args],
        cwd=ROOT,
        text=True,
    )


def main() -> None:
    data = json.loads(GUIDANCE.read_text(encoding="utf-8"))

    assert data["schema"] == "trinityaccord.record-chain-agent-field-guidance.v1"
    assert "correction" in data["record_types"]
    assert "guardian_retirement" in data["record_types"]
    assert "correction_content.target_record_sha256" in data["fields"]
    assert "target_guardian_application_record_sha256" in data["fields"]

    target_sha = data["fields"]["correction_content.target_record_sha256"]
    assert target_sha["source_of_truth"].endswith("record_sha256")
    assert "content_sha256" in target_sha["never_use"]
    assert "content_sha256_v2" in target_sha["never_use"]
    assert target_sha["unclear_action"] == "BUILDER_USAGE_UNCLEAR"

    correction_output = run_cli("record-type", "correction")
    assert "--target-record-id" in correction_output
    assert "--target-record-sha256" in correction_output
    assert "BUILDER_USAGE_UNCLEAR" in correction_output

    field_output = run_cli("field", "correction_content.target_record_sha256")
    assert "record_sha256" in field_output
    assert "Never use" in field_output
    assert "content_sha256" in field_output
    assert "BUILDER_USAGE_UNCLEAR" in field_output

    guardian_output = run_cli("record-type", "guardian-retirement")
    assert "--target-guardian-application-record-id" in guardian_output
    assert "--target-guardian-application-record-sha256" in guardian_output

    print("agent submit guidance contract OK")


if __name__ == "__main__":
    main()
