from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "record_chain_intake_gateway"))

from gateway.authorship import GATEWAY_DERIVED_UNSIGNED_FIELDS, UNSIGNED_PROJECTION_FIELDS  # noqa: E402


def test_gateway_derived_unsigned_fields_are_narrow() -> None:
    assert GATEWAY_DERIVED_UNSIGNED_FIELDS == {"created_at"}


def test_projection_fields_include_append_assigned_integrity_fields() -> None:
    expected = {
        "actor_identity",
        "boundary",
        "boundary_acknowledgement",
        "server_normalization",
        "server_append_metadata",
        "append_assigned_metadata",
        "authorship_verification_status",
        "record_id",
        "record_index",
        "assigned_at",
        "previous_record_sha256",
        "content_sha256",
        "content_sha256_v2",
        "record_sha256",
        "chain_id",
        "what_i_checked",
        "limitations",
        "related_records",
        "immutability_policy",
    }
    assert expected <= UNSIGNED_PROJECTION_FIELDS


def test_signed_payload_scope_doc_names_recovery_fields() -> None:
    doc = (ROOT / "docs" / "record-chain-signed-payload-scope.md").read_text(encoding="utf-8")
    for field in GATEWAY_DERIVED_UNSIGNED_FIELDS:
        assert f"`{field}`" in doc
    for field in ("created_at", "authorship_proof", "proof"):
        assert f"`{field}`" in doc
    assert "must include\nthe oath/declaration fields in `record_draft` before authorship signing" in doc
