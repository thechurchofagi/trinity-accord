from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TYPES = ["echo", "verification", "guardian_application", "guardian_retirement", "propagation", "correction", "classification_update", "context_insufficient_notice"]
FORMAL = TYPES[:-1]
FLAGS = ["--verification-level", "--what-was-checked", "--verification-claim", "--fresh-actions", "--digital-profile", "--relationships-checked", "--physical-observation", "--external-witness", "--coverage-scope", "--limitations", "--claims-not-made", "--corrections-or-supersession-checked"]


def load(path: str) -> dict[str, Any]:
    value = json.loads((ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def verified_builder_runtime() -> str:
    manifest = load("api/record-chain-builder-bundles.v1.json")
    canonical = manifest["canonical_builder"]
    layers = [
        (ROOT / "downloads/record-chain-builder.mjs", canonical),
        (
            ROOT / "downloads/record-chain-builder-recovery.mjs",
            canonical["recovery_wrapper"],
        ),
        (
            ROOT / "downloads/record-chain-builder-core.mjs",
            canonical["core"],
        ),
    ]
    texts: list[str] = []
    for path, contract in layers:
        data = path.read_bytes()
        assert hashlib.sha256(data).hexdigest() == contract["sha256"]
        assert len(data) == contract["size_bytes"]
        texts.append(data.decode("utf-8"))
    return "\n".join(texts)


def walk(value: Any):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def schema_types() -> set[str]:
    schema = load("api/record-chain-submission-schema.v1.json")
    matches = []
    for value in walk(schema):
        if isinstance(value, dict) and isinstance(value.get("enum"), list) and set(TYPES).issubset(set(value["enum"])):
            matches.append(set(value["enum"]))
    assert matches
    return min(matches, key=len)


def test_record_types_match_runtime_contracts_and_schema() -> None:
    for path in ("api/agent-first-contact.json", "api/agent-start.v2.json", "api/record-chain-intake-gateway.v1.json", "downloads/record-chain-agent-field-guidance.v1.json"):
        source = load(path)["runtime_alignment"]
        assert source["accepted_record_types"] == TYPES
        assert source["formal_oath_record_types"] == FORMAL
    assert schema_types() == set(TYPES)
    runtime = (ROOT / "apps/record_chain_intake_gateway/gateway/validation.py").read_text(encoding="utf-8")
    for record_type in TYPES:
        assert f'"{record_type}"' in runtime


def test_gateway_routes_and_base_url_match() -> None:
    app = (ROOT / "apps/record_chain_intake_gateway/app.py").read_text(encoding="utf-8")
    builder = verified_builder_runtime()
    contract = load("api/record-chain-intake-gateway.v1.json")
    base = "https://trinity-record-chain-gateway.onrender.com"
    for route in ("/healthz", "/record-chain/readiness", "/record-chain/preflight", "/record-chain/submit", "/record-chain/receipt/{receipt_id}"):
        assert route in app
    assert base in builder
    assert contract["base_url"] == base


def test_verification_examples_include_runtime_required_flags() -> None:
    builder = verified_builder_runtime()
    quick = (ROOT / "external-agent-quickstart.md").read_text(encoding="utf-8")
    command = load("api/agent-task-router.v1.json")["routes"]["verify_current_model"]["builder_command"]
    for flag in FLAGS:
        assert flag in builder
        assert flag in quick
        assert flag in command


def test_builder_local_validation_matches_gateway() -> None:
    builder = verified_builder_runtime()
    runtime = (ROOT / "apps/record_chain_intake_gateway/gateway/validation.py").read_text(encoding="utf-8")
    assert 'command === "context-insufficient"' in builder
    assert 'requireExplicit(opts, "body", "--body or --body-file")' in builder
    assert "MISSING_CONTEXT_INSUFFICIENT_REASON" in runtime
    assert "minimumContextLevelForAction(opts.recordType)" in builder
    assert "Formal public records require --context-sufficient-for-selected-action true" in builder
    assert "--loaded-urls is required for every formal record" in builder
    assert "classification_update, context_insufficient_notice" in builder


def test_builder_manifest_matches_exact_bytes() -> None:
    manifest = load("api/record-chain-builder-bundles.v1.json")
    data = (ROOT / "downloads/record-chain-builder.mjs").read_bytes()
    assert manifest["canonical_builder"]["sha256"] == hashlib.sha256(data).hexdigest()
    assert manifest["canonical_builder"]["size_bytes"] == len(data)
    assert set(TYPES).issubset(set(manifest["canonical_builder"]["supports"]))
