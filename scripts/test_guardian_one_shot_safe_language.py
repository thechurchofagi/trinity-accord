#!/usr/bin/env python3
"""Ensure one-shot Guardian application text does not trigger forbidden archive claims."""

import json
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "scripts" / "create_guardian_application.mjs"
DIGEST = ROOT / "scripts" / "proof_payload_digest.mjs"
ARCHIVE_GATE = ROOT / "scripts" / "archive_readiness_gate.py"

FORBIDDEN_IN_NATURAL_LANGUAGE = [
    "archived echo",
    "verified record",
    "successor reception",
    "independent attestation",
    "amendment",
]


def run(cmd):
    result = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, result.stderr or result.stdout
    return result


def natural_language_fields(payload):
    fields = []
    def add(path, value):
        if isinstance(value, str) and value.strip():
            fields.append((path, value))

    add("title", payload.get("title"))
    add("body", payload.get("body"))

    for i, value in enumerate(payload.get("what_i_checked", [])):
        add(f"what_i_checked[{i}]", value)

    for i, value in enumerate(payload.get("limitations", [])):
        add(f"limitations[{i}]", value)

    integrity = payload.get("agent_integrity_declaration", {})
    add("agent_integrity_declaration.declaration_text", integrity.get("declaration_text"))

    oath = integrity.get("verification_oath", {})
    add("agent_integrity_declaration.verification_oath.agent_readback", oath.get("agent_readback"))

    reg = payload.get("guardian_registration", {})
    add("guardian_registration.declared_intent", reg.get("declared_intent"))

    for i, applicant in enumerate(reg.get("joint_applicants", [])):
        add(f"guardian_registration.joint_applicants[{i}].participation_note", applicant.get("participation_note"))

    return fields


def main():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        out = td / "guardian-application.final.json"
        key_dir = td / "keys"

        run([
            "node", str(BUILDER),
            "--mode", "joint_human_ai",
            "--signing-key-holder", "ai_agent_key_holder",
            "--human-label", "Test Human",
            "--agent-label", "Test Agent",
            "--agent-provider", "Test Runtime",
            "--title", "Guardian Alliance Joint Human-AI Application Test",
            "--challenge", "guardian-application-test",
            "--created-at", "2026-05-22T00:00:00.000Z",
            "--key-dir", str(key_dir),
            "--out", str(out),
        ])

        data = json.loads(out.read_text(encoding="utf-8"))

        hits = []
        for path, value in natural_language_fields(data):
            lower = value.lower()
            for phrase in FORBIDDEN_IN_NATURAL_LANGUAGE:
                if phrase in lower:
                    hits.append((path, phrase, value))

        assert not hits, "Forbidden archive-claim phrases in natural language: " + repr(hits)

        # Machine fields may contain schema terms such as not_amendment or not_successor_reception.
        assert data["boundary_acknowledgement"]["not_amendment"] is True
        assert data["guardian_registration"]["boundaries"]["not_successor_reception"] is True

        digest = json.loads(run(["node", str(DIGEST), "--payload", str(out)]).stdout)
        expected_digest = digest["proof_payload_sha256"]
        assert data["guardian_presence_proof"]["signed_payload_sha256"] == expected_digest
        assert data["authorship_proof"]["signed_payload_sha256"] == expected_digest

        archive = run([
            "python3", str(ARCHIVE_GATE),
            "--gateway-payload", str(out),
            "--json",
        ])

        archive_body = json.loads(archive.stdout)
        assert archive_body.get("archive_ready") is True, archive.stdout

    print("GUARDIAN_ONE_SHOT_SAFE_LANGUAGE_OK")


if __name__ == "__main__":
    main()
