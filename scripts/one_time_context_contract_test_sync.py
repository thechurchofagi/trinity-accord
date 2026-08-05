#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(path: str, old: str, new: str) -> None:
    target = ROOT / path
    text = target.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{path}: expected one replacement, found {count}")
    target.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    "tests/test_external_agent_builder_resilience.py",
    '''def test_external_agent_builder_v23_is_manifest_bound():
    manifest = json.loads(
        (ROOT / "api" / "record-chain-builder-bundles.v1.json").read_text(encoding="utf-8")
    )["canonical_builder"]["core"]
    core_bytes = BUILDER.read_bytes()
    core_text = core_bytes.decode("utf-8")
    assert 'const BUILDER_VERSION = "v2.3"' in core_text
    assert hashlib.sha256(core_bytes).hexdigest() == manifest["sha256"]
    assert len(core_bytes) == manifest["size_bytes"]
''',
    '''def test_external_agent_builder_v24_is_manifest_bound():
    manifest = json.loads(
        (ROOT / "api" / "record-chain-builder-bundles.v1.json").read_text(encoding="utf-8")
    )["canonical_builder"]["core"]
    core_bytes = BUILDER.read_bytes()
    core_text = core_bytes.decode("utf-8")
    assert 'const BUILDER_VERSION = "v2.4"' in core_text
    assert "minimumContextLevelForAction(opts.recordType)" in core_text
    assert hashlib.sha256(core_bytes).hexdigest() == manifest["sha256"]
    assert len(core_bytes) == manifest["size_bytes"]
''',
)

(ROOT / "tests/test_gateway_context_readiness.py").write_text(
    '''from apps.record_chain_intake_gateway.gateway.validation import validate_context_readiness


def _base_verification_draft(
    level: str,
    cc: str,
    *,
    minimum: str = "CC-3",
    sufficient: bool = True,
    read_confirmed: bool = True,
):
    return {
        "record_type": "verification",
        "verification_content": {
            "verification_level": level,
            "verification_scope_label": "test",
            "what_was_checked": ["test"],
            "verification_claim": "test",
            "fresh_actions_performed": ["test"],
        },
        "context_readiness": {
            "declared_context_level": cc,
            "minimum_required_for_action": minimum,
            "context_sufficient_for_selected_action": sufficient,
            "loaded_context_urls": ["https://www.trinityaccord.org/agent-start/"],
            "context_read_confirmed": read_confirmed,
        },
    }


def test_public_verification_v2_rejects_cc2():
    diagnostics = validate_context_readiness(
        "verification", _base_verification_draft("V2", "CC-2")
    )
    assert any(d.code == "INSUFFICIENT_CONTEXT_COMPLETENESS" for d in diagnostics)


def test_public_verification_v2_accepts_honest_cc3():
    diagnostics = validate_context_readiness(
        "verification", _base_verification_draft("V2", "CC-3")
    )
    forbidden = {
        "INSUFFICIENT_CONTEXT_COMPLETENESS",
        "CONTEXT_NOT_SUFFICIENT_FOR_FORMAL_RECORD",
        "CC3_CONTEXT_READ_CONFIRMATION_REQUIRED",
        "MINIMUM_REQUIRED_FOR_ACTION_UNDERSTATED",
    }
    assert not any(d.code in forbidden for d in diagnostics)


def test_public_verification_v3_requires_cc3():
    diagnostics = validate_context_readiness(
        "verification", _base_verification_draft("V3", "CC-2")
    )
    assert any(d.code == "INSUFFICIENT_CONTEXT_COMPLETENESS" for d in diagnostics)


def test_cc6_rejected():
    diagnostics = validate_context_readiness("echo", {
        "record_type": "echo",
        "context_readiness": {
            "declared_context_level": "CC-6",
            "minimum_required_for_action": "CC-3",
            "context_sufficient_for_selected_action": True,
            "loaded_context_urls": ["https://www.trinityaccord.org/agent-echo/"],
            "context_read_confirmed": True,
        },
    })
    assert any(d.code == "INVALID_CONTEXT_LEVEL_RANGE" for d in diagnostics)
''',
    encoding="utf-8",
)

replace_once(
    "tests/test_machine_entry_runtime_alignment.py",
    '''    assert "CONTEXT_HONESTY_LEVELS.has(String(opts.contextLevel).toUpperCase())" in builder
    assert "CC-3, CC-4, or CC-5" in builder
    assert "classification_update, context_insufficient_notice" in builder
''',
    '''    assert "minimumContextLevelForAction(opts.recordType)" in builder
    assert "Formal public records require --context-sufficient-for-selected-action true" in builder
    assert "--loaded-urls is required for every formal record" in builder
    assert "classification_update, context_insufficient_notice" in builder
''',
)

replace_once(
    "tests/test_record_chain_submit_recovery.py",
    '''CORE_SHA256 = "269bdd593455b73fa4bb39e24b6805a07abc2e783eeb388ea84e87d15dcf42bc"
CORE_SIZE_BYTES = 208440
''',
    '''CORE_SHA256 = "2d2a417561bf470974da81e6cc3c8553368c6c9976bb5748861f243f2c21891e"
CORE_SIZE_BYTES = 209852
''',
)

helper_path = ROOT / "api/record-chain-field-helper.v1.json"
helper = json.loads(helper_path.read_text(encoding="utf-8"))
help_map = helper.get("diagnostic_code_help")
if not isinstance(help_map, dict):
    raise SystemExit("diagnostic_code_help missing")
helper["diagnostic_code_help"] = {key: help_map[key] for key in sorted(help_map)}
helper_path.write_text(json.dumps(helper, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Synchronized context contract tests and sorted diagnostic help.")
