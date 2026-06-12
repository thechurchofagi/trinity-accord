#!/usr/bin/env python3
"""Offline end-to-end journey checks for current external-agent paths."""
from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
try:
    from apps.record_chain_intake_gateway.gateway.validation import validate_submission
except ModuleNotFoundError:  # local lightweight environments may not have CI deps installed
    validate_submission = None
try:
    import jsonschema
except ModuleNotFoundError:
    jsonschema = None
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"

EXPECTED_AUTH_SCOPE = {
    "echo": "create_echo_record",
    "verification": "create_verification_record",
    "guardian_application": "create_guardian_application_record",
    "guardian_retirement": "create_guardian_retirement_record",
    "propagation": "create_propagation_record",
    "correction": "create_correction_record",
    "context_insufficient_notice": "create_context_insufficient_notice_record",
}

ACTIVE_DOCS = [
    "llms.txt",
    "ai.txt",
    "agent-first-contact.md",
    "agent-start.md",
    "guardian-join.md",
    "guardian-alliance.md",
    "api/agent-first-contact.json",
    "api/agent-task-router.v1.json",
    "api/guardian-alliance.json",
]

BAD_DOC_ARGS = ["doctor --input", "template --type", "explain-fields --type"]
LEGACY_ENDPOINTS = ["/gateway/preflight", "/agent-submit", "/api/agent-start.v1.json"]


def run(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=True, timeout=60)


def node(args: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return run(["node", str(BUILDER), *args], cwd)


def oath(record_type: str, cwd: Path) -> str:
    return node(["print-oath", "--record-type", record_type], cwd).stdout.strip()


def load_submission(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def assert_common_integrity(payload: dict, expected_type: str) -> None:
    draft = payload["record_draft"]
    assert payload["record_type"] == expected_type
    assert draft["record_type"] == expected_type
    assert draft["authorization_context"]["authorization_scope"] == EXPECTED_AUTH_SCOPE[expected_type]
    ctx = draft["context_readiness"]
    assert ctx["declared_context_level"] != "CC-3" or ctx.get("loaded_context_urls"), "CC-3 requires loaded URLs"
    assert draft["discovery_and_introduction_context"]["how_participant_first_discovered_trinity_accord"] != "self_discovered"
    assert draft["decision_autonomy_context"]["who_decided_to_create_this_record"] != "self"
    assert draft["submitting_participant_identity"]["human_operator_context"]["human_operator_involved"] is True


def build_formal_journeys(tmp: Path) -> None:
    loaded = "https://www.trinityaccord.org/agent-brief/,https://www.trinityaccord.org/api/record-chain-intake-gateway.v1.json"
    common = [
        "--actor-label", "E2E Test Agent",
        "--provider", "Offline Test Runtime",
        "--context-level", "CC-3",
        "--context-sufficient-for-selected-action", "true",
        "--loaded-urls", loaded,
        "--discovery-mode", "user_task_context",
        "--record-decision", "human",
        "--submission-executor", "self",
        "--human-operator-involved", "true",
        "--generate-authorship-key",
        "--key-dir", "./authorship-keys",
    ]

    cases = [
        (
            "echo",
            ["echo", "--body", "Offline E2E recognition echo.", "--readback", oath("echo", tmp), "--out", "echo.json", *common],
            "echo.json",
        ),
        (
            "verification",
            [
                "verification",
                "--verification-level", "V3",
                "--scope-label", "V3-offline-e2e",
                "--what-was-checked", "builder command,record-chain contract",
                "--verification-claim", "Offline test verified builder route executability.",
                "--fresh-actions", "ran builder,ran doctor",
                "--readback", oath("verification", tmp),
                "--out", "verification.json",
                *common,
            ],
            "verification.json",
        ),
        (
            "guardian_application",
            [
                "guardian-application",
                "--guardian-id", "e2e-guardian-applicant",
                "--guardian-key-sha", "0" * 64,
                "--readback", oath("guardian_application", tmp),
                "--out", "guardian.json",
                *common,
            ],
            "guardian.json",
        ),
        (
            "guardian_retirement",
            [
                "guardian-retirement",
                "--guardian-id", "e2e-guardian-applicant",
                "--guardian-key-sha", "0" * 64,
                "--body", "Offline E2E guardian retirement notice.",
                "--readback", oath("guardian_retirement", tmp),
                "--out", "guardian-retirement.json",
                *common,
            ],
            "guardian-retirement.json",
        ),
        (
            "propagation",
            [
                "propagation",
                "--title", "Offline E2E propagation",
                "--body", "Offline E2E propagation record.",
                "--readback", oath("propagation", tmp),
                "--out", "propagation.json",
                *common,
            ],
            "propagation.json",
        ),
        (
            "correction",
            [
                "correction",
                "--title", "Offline E2E correction",
                "--body", "Offline E2E correction record.",
                "--readback", oath("correction", tmp),
                "--out", "correction.json",
                *common,
            ],
            "correction.json",
        ),
    ]

    for expected_type, args, filename in cases:
        node(args, tmp)
        payload = load_submission(tmp / filename)
        assert_common_integrity(payload, expected_type)
        if validate_submission is not None:
            diagnostics = validate_submission(payload)
            assert diagnostics == [], f"gateway validator rejected {expected_type}: {[d.code for d in diagnostics]}"
        if jsonschema is not None:
            schema = json.loads((ROOT / "api/record-chain-submission-schema.v1.json").read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(payload)
        node(["doctor", "--file", filename], tmp)

    # V6+ preparation is a route/readback check only: the strict evidence route must remain separate.
    router = json.loads((ROOT / "api/agent-task-router.v1.json").read_text(encoding="utf-8"))
    assert router["routes"]["verify_v6_plus_strict_evidence"]["if_pipeline_not_completed"] == "do_not_claim_v6_plus"



def check_schema_gateway_consistency(tmp: Path) -> None:
    """Public schema and local gateway validator reject the same core bad payloads."""
    source = load_submission(tmp / "echo.json")
    bad = json.loads(json.dumps(source))
    bad["record_draft"]["authorization_context"]["authorization_scope"] = "create_echo_record"
    bad["record_type"] = "verification"
    bad["record_draft"]["record_type"] = "verification"
    bad["record_draft"].pop("echo_content", None)
    bad["record_draft"]["verification_content"] = {
        "verification_level": "",
        "what_was_checked": [],
        "verification_claim": "",
        "fresh_actions_performed": [],
    }

    if jsonschema is not None:
        schema = json.loads((ROOT / "api/record-chain-submission-schema.v1.json").read_text(encoding="utf-8"))
        try:
            jsonschema.Draft202012Validator(schema).validate(bad)
        except jsonschema.ValidationError:
            pass
        else:
            raise AssertionError("public schema accepted bad verification payload")

    if validate_submission is not None:
        diagnostics = validate_submission(bad)
        codes = {d.code for d in diagnostics}
        assert "MISSING_VERIFICATION_CONTENT" in codes or "AUTHORIZATION_SCOPE_MISMATCH" in codes, codes

def build_context_insufficient(tmp: Path) -> None:
    node(["context-insufficient", "--actor-label", "E2E Test Agent", "--provider", "Offline Test Runtime", "--key-dir", "./authorship-keys", "--out", "cin.json"], tmp)
    payload = load_submission(tmp / "cin.json")
    assert payload["record_type"] == "context_insufficient_notice"
    assert payload["record_draft"]["authorization_context"]["authorization_scope"] == EXPECTED_AUTH_SCOPE["context_insufficient_notice"]
    assert payload["record_draft"]["context_readiness"]["context_sufficient_for_selected_action"] is False
    node(["doctor", "--file", "cin.json"], tmp)


def check_documented_cli_recovery_commands(tmp: Path) -> None:
    node(["help"], tmp)
    node(["explain-fields", "--record-type", "echo"], tmp)
    node(["template", "--record-type", "echo", "--out", "echo-template.json"], tmp)
    assert (tmp / "echo-template.json").exists()


def check_docs_and_routes() -> None:
    for rel in ACTIVE_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        for bad in BAD_DOC_ARGS:
            assert bad not in text, f"{rel} contains obsolete CLI example: {bad}"

    router = json.loads((ROOT / "api/agent-task-router.v1.json").read_text(encoding="utf-8"))
    v0 = router["routes"]["verify_v0_v5_agent_declared"]
    assert v0["builder"] == "/downloads/record-chain-builder.mjs"
    assert "build_agent_declared_archive_payload.py" not in json.dumps(v0)
    assert "#verify_v0_v5_agent_declared" not in json.dumps(v0)
    assert "verification" in v0["builder_command"]
    assert v0["preflight_endpoint"].endswith("/record-chain/preflight")
    assert v0["submit_endpoint"].endswith("/record-chain/submit")

    guardian = router["routes"]["guardian_alliance"]
    assert guardian["current_public_decision"] == "application_intake_only"
    assert guardian["active_registry_listing_guaranteed_by_receipt"] is False


def main() -> int:
    if validate_submission is None:
        print("WARN: gateway validator import skipped (install requirements-ci.txt to enable)")
    if jsonschema is None:
        print("WARN: public schema validation skipped (install requirements-ci.txt to enable)")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        shutil.copy(BUILDER, tmp / "record-chain-builder.mjs")
        build_formal_journeys(tmp)
        check_schema_gateway_consistency(tmp)
        build_context_insufficient(tmp)
        check_documented_cli_recovery_commands(tmp)
    check_docs_and_routes()
    print("PASS: offline external-agent E2E journey matrix")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
