"""Part A: record_type consistency and envelope alias rejection tests."""
from __future__ import annotations

import pytest
from gateway.validation import (
    detect_route,
    extract_record_draft,
    normalize_record_type_value,
    record_draft_value,
    validate_envelope_aliases_and_record_type,
    validate_submission,
    _DRAFT_MISSING,
)


# ---------------------------------------------------------------------------
# normalize_record_type_value
# ---------------------------------------------------------------------------

class TestNormalizeRecordTypeValue:
    def test_basic(self):
        assert normalize_record_type_value("echo") == "echo"

    def test_uppercase(self):
        assert normalize_record_type_value("Echo") == "echo"

    def test_hyphen_to_underscore(self):
        assert normalize_record_type_value("guardian-application") == "guardian_application"

    def test_whitespace_strip(self):
        assert normalize_record_type_value("  echo  ") == "echo"

    def test_non_string(self):
        assert normalize_record_type_value(42) == ""
        assert normalize_record_type_value(None) == ""
        assert normalize_record_type_value(True) == ""


# ---------------------------------------------------------------------------
# record_draft_value / extract_record_draft
# ---------------------------------------------------------------------------

class TestRecordDraftValue:
    def test_missing_returns_sentinel(self):
        assert record_draft_value({}) is _DRAFT_MISSING

    def test_present_returns_value(self):
        d = {"record_draft": {"x": 1}}
        assert record_draft_value(d) == {"x": 1}

    def test_none_returns_none(self):
        assert record_draft_value({"record_draft": None}) is None


class TestExtractRecordDraft:
    def test_missing_returns_none(self):
        assert extract_record_draft({}) is None

    def test_non_dict_returns_none(self):
        assert extract_record_draft({"record_draft": "not a dict"}) is None

    def test_dict_returned(self):
        d = {"record_type": "echo"}
        assert extract_record_draft({"record_draft": d}) is d


# ---------------------------------------------------------------------------
# validate_envelope_aliases_and_record_type
# ---------------------------------------------------------------------------

class TestEnvelopeAliases:
    def _base(self, **overrides):
        sub = {"record_type": "echo", "record_draft": {"record_type": "echo"}}
        sub.update(overrides)
        return sub

    def test_valid_passes(self):
        sub = self._base()
        diags = validate_envelope_aliases_and_record_type(sub, extract_record_draft(sub))
        assert diags == []

    def test_draft_alias_rejected(self):
        sub = self._base()
        sub["draft"] = sub.pop("record_draft")
        diags = validate_envelope_aliases_and_record_type(sub, None)
        assert any(d.code == "DRAFT_ALIAS_RETIRED" for d in diags)

    def test_type_alias_rejected(self):
        sub = self._base()
        sub["type"] = "echo"
        diags = validate_envelope_aliases_and_record_type(sub, extract_record_draft(sub))
        assert any(d.code == "TYPE_ALIAS_RETIRED" for d in diags)

    def test_record_type_mismatch(self):
        sub = self._base(record_type="echo")
        sub["record_draft"] = {"record_type": "verification"}
        diags = validate_envelope_aliases_and_record_type(sub, extract_record_draft(sub))
        assert any(d.code == "RECORD_TYPE_MISMATCH" for d in diags)

    def test_missing_record_type(self):
        sub = {"record_draft": {"record_type": "echo"}}
        diags = validate_envelope_aliases_and_record_type(sub, extract_record_draft(sub))
        assert any(d.code == "MISSING_RECORD_TYPE" for d in diags)

    def test_missing_draft_record_type(self):
        sub = {"record_type": "echo", "record_draft": {}}
        diags = validate_envelope_aliases_and_record_type(sub, extract_record_draft(sub))
        assert any(d.code == "MISSING_DRAFT_RECORD_TYPE" for d in diags)


# ---------------------------------------------------------------------------
# detect_route
# ---------------------------------------------------------------------------

class TestDetectRoute:
    def test_valid_echo(self):
        assert detect_route({"record_type": "echo", "record_draft": {"record_type": "echo"}}) == "echo"

    def test_mismatch_returns_unknown(self):
        assert detect_route({"record_type": "echo", "record_draft": {"record_type": "verification"}}) == "unknown"

    def test_draft_alias_returns_unknown(self):
        assert detect_route({"record_type": "echo", "draft": {}}) == "unknown"

    def test_type_alias_returns_unknown(self):
        assert detect_route({"type": "echo", "record_draft": {"record_type": "echo"}}) == "unknown"

    def test_unknown_type(self):
        assert detect_route({"record_type": "bogus", "record_draft": {"record_type": "bogus"}}) == "unknown"


# ---------------------------------------------------------------------------
# Full validate_submission integration
# ---------------------------------------------------------------------------

class TestValidateSubmissionAliases:
    def _valid_base(self):
        return {
            "record_type": "echo",
            "record_draft": {
                "schema": "trinityaccord.record-chain-entry-draft.v2",
                "record_type": "echo",
            },
            "submission_boundary": {f: True for f in [
                "not_authority", "not_governance", "not_attestation",
                "not_successor_reception", "not_amendment", "bitcoin_originals_prevail",
                "receipt_is_not_final_inclusion", "receipt_is_intake_only",
                "later_records_may_reclassify_or_correct_this_record",
            ]},
        }

    def test_preflight_rejects_draft_alias(self):
        sub = self._valid_base()
        sub["draft"] = sub["record_draft"]
        diags = validate_submission(sub)
        assert any(d.code == "DRAFT_ALIAS_RETIRED" for d in diags)

    def test_preflight_rejects_type_alias(self):
        sub = self._valid_base()
        sub["type"] = "echo"
        diags = validate_submission(sub)
        assert any(d.code == "TYPE_ALIAS_RETIRED" for d in diags)

    def test_preflight_rejects_type_mismatch(self):
        sub = self._valid_base()
        sub["record_draft"] = {"record_type": "verification"}
        diags = validate_submission(sub)
        assert any(d.code == "RECORD_TYPE_MISMATCH" for d in diags)

    def test_preflight_rejects_non_object_record_draft(self):
        sub = self._valid_base()
        sub["record_draft"] = "not an object"
        diags = validate_submission(sub)
        assert any(d.code == "INVALID_DRAFT" for d in diags)

    def test_preflight_rejects_draft_alias_even_with_record_draft(self):
        sub = self._valid_base()
        sub["draft"] = {"record_type": "echo"}
        diags = validate_submission(sub)
        assert any(d.code == "DRAFT_ALIAS_RETIRED" for d in diags)
