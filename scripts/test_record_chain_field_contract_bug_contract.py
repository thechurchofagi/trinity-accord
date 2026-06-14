#!/usr/bin/env python3
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fail(message: str) -> None:
    print(f"FAIL: {message}", file=sys.stderr)
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def read(path: str) -> str:
    p = ROOT / path
    require(p.exists(), f"missing {path}")
    return p.read_text(encoding="utf-8")


def load_json(path: str) -> dict:
    return json.loads(read(path))


def main() -> None:
    app = read("apps/record_chain_intake_gateway/app.py")
    authorship = read("apps/record_chain_intake_gateway/gateway/authorship.py")
    validation = read("apps/record_chain_intake_gateway/gateway/validation.py")
    models = read("apps/record_chain_intake_gateway/gateway/models.py")
    builder = read("downloads/record-chain-builder.mjs")
    submission_schema = load_json("api/record-chain-submission-schema.v1.json")
    submit_schema = load_json("api/record-chain-submit-response.v1.json")

    for label, text in [
        ("app.py", app),
        ("authorship.py", authorship),
        ("validation.py", validation),
        ("models.py", models),
    ]:
        try:
            ast.parse(text)
        except SyntaxError as exc:
            fail(f"{label} syntax error: {exc}")

    schema_text = json.dumps(submission_schema, ensure_ascii=False, sort_keys=True)

    # A: server_append_metadata must be rejected before it can enter signed client draft flow.
    require('"server_append_metadata"' in app, "app.py must reject client-supplied server_append_metadata")
    require('"server_append_metadata"' in schema_text, "submission schema must forbid record_draft.server_append_metadata")

    # B: claim_boundary must be validated through top-level authorship_proof verifier.
    require(
        "boundary_err = _check_claim_boundary(proof)" in authorship,
        "verify_authorship_proof_submission must call _check_claim_boundary(proof)",
    )
    require(
        "diagnostics.extend(validate_claim_boundary(draft))" not in validation,
        "validate_submission must not call stale draft-level claim_boundary validation",
    )

    # C: classification_update must be a complete supported record type.
    require('"classification_update"' in schema_text, "submission schema must include classification_update")
    require('"classification_update_content"' in schema_text, "classification_update schema must require classification_update_content")

    required_classification_fields = [
        "target_record_id",
        "target_record_sha256",
        "previous_classification",
        "new_classification",
        "classification_reason",
        "evidence_or_review_basis",
    ]
    for field in required_classification_fields:
        require(field in schema_text, f"classification_update schema missing {field}")
        require(field in builder, f"builder missing classification update field {field}")
        require(field in validation, f"gateway validation missing classification update field {field}")

    require("function buildClassificationUpdateDraft" in builder, "builder must define buildClassificationUpdateDraft")
    require('"classification-update": buildClassificationUpdateDraft' in builder, "builder must register classification-update command")
    require('record_type: "classification_update"' in builder, "builder must emit record_type classification_update")
    require('record_type == "classification_update"' in validation, "gateway must validate classification_update content")
    require('"guardian-key-rotation":' not in builder, "this task must not add guardian-key-rotation builder command")

    # D: submit response schema must accept actual server statuses and model default.
    require('append_status: str = "not_applicable"' in models, "SubmitResponse append_status default must be not_applicable")
    append_status_enum = submit_schema["properties"]["append_status"]["enum"]
    for status in [
        "not_applicable",
        "pending",
        "duplicate_existing_submission_returned",
        "duplicate_existing_receipt_returned",
    ]:
        require(status in append_status_enum, f"submit response schema missing append_status {status}")

    # E: normal endpoint response boundaries must include endpoint-specific keys.
    require("def _build_preflight_boundary" in app, "app.py must define _build_preflight_boundary")
    require("def _build_submit_boundary" in app, "app.py must define _build_submit_boundary")
    for key in [
        "preflight_is_not_submission",
        "receipt_is_not_authority",
        "receipt_is_not_attestation",
        "receipt_is_not_final_chain_record",
        "record_chain_append_is_server_side",
    ]:
        require(key in app, f"app.py missing response boundary key {key}")

    require("_build_preflight_boundary(body)" in app, "preflight normal response must use _build_preflight_boundary(body)")
    require("_build_submit_boundary(body)" in app, "submit responses must use _build_submit_boundary(body)")

    print("PASS: record-chain field-contract bug contract")


if __name__ == "__main__":
    main()
