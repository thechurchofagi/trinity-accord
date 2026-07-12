from pathlib import Path

from apps.record_chain_intake_gateway.gateway.validation import redact_transient_oath_readback


ROOT = Path(__file__).resolve().parents[3]


def test_redaction_removes_raw_readback_without_mutating_input() -> None:
    submission = {
        "record_type": "echo",
        "record_draft": {"record_type": "echo"},
        "client_oath_readback": {
            "schema": "trinityaccord.client-oath-readback.v1",
            "record_type": "echo",
            "oath_policy_sha256": "a" * 64,
            "oath_modules": ["common_submission_integrity_v1"],
            "readback_text": "line one\r\nline two  ",
            "readback_text_sha256": "stale",
        },
    }
    redacted = redact_transient_oath_readback(submission)
    assert submission["client_oath_readback"]["readback_text"] == "line one\r\nline two  "
    stored = redacted["client_oath_readback"]
    assert "readback_text" not in stored
    assert stored["redacted_after_gateway_validation"] is True
    assert stored["readback_text_hash_canonicalization"] == "NFC_CRLF_TO_LF_STRIP"
    assert len(stored["readback_text_sha256"]) == 64
    assert stored["readback_text_char_count"] == len("line one\nline two")


def test_submit_persists_only_redacted_submission() -> None:
    source = (ROOT / "apps" / "record_chain_intake_gateway" / "app.py").read_text(encoding="utf-8")
    assert "stored_submission = redact_transient_oath_readback(body)" in source
    assert "stored_submission_sha256 = sha256_canonical_json(stored_submission)" in source
    assert "submission=stored_submission" in source
    assert "submission_content = canonical_dumps(stored_submission)" in source
    assert "submission_content = canonical_dumps(body)" not in source
