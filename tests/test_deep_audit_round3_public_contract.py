from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_round3_submit_discriminator_is_unambiguous() -> None:
    public_path = ROOT / "api/record-chain-submit-response.v1.json"
    shadow_path = (
        ROOT
        / "apps/record_chain_intake_gateway/schemas/submit_response.schema.json"
    )
    schema = json.loads(public_path.read_text(encoding="utf-8"))
    assert schema["$defs"]["success"]["properties"]["duplicate"] == {"const": False}
    assert schema["$defs"]["duplicate"]["properties"]["duplicate"] == {"const": True}
    assert "duplicate" in schema["$defs"]["success"]["required"]
    assert "duplicate" in schema["$defs"]["duplicate"]["required"]
    assert shadow_path.read_bytes() == public_path.read_bytes()


def test_round3_receipt_and_atomic_truthfulness_guards_remain_active() -> None:
    app_source = (
        ROOT / "apps/record_chain_intake_gateway/app.py"
    ).read_text(encoding="utf-8")
    atomic_source = (
        ROOT / "apps/record_chain_intake_gateway/gateway/github_atomic.py"
    ).read_text(encoding="utf-8")

    assert "_record_chain_record_sha256" in app_source
    assert "RECEIPT_NON_DURABLE_DRY_RUN" in app_source
    assert "INTAKE_ATOMIC_CONFLICT_LOOKUP_FAILED" in app_source
    assert "parse_json_strict(receipt_text)" in app_source
    assert "_authoritative_reconciled_commit_sha" in atomic_source
    assert "reconciled_after_response" in atomic_source


def test_round3_one_shot_machinery_is_absent() -> None:
    for relative in (
        "scripts/apply_deep_audit_round3.py",
        "scripts/align_deep_audit_round3_tests.py",
        "scripts/fix_deep_audit_round3_test_expectations.py",
        "scripts/fix_deep_audit_round3_dry_run_cache.py",
        ".github/workflows/apply-deep-audit-round3.yml",
        ".github/workflows/sync-round3-submit-shadow.yml",
    ):
        assert not (ROOT / relative).exists(), relative
