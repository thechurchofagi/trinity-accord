from apps.record_chain_intake_gateway.gateway.validation import redact_transient_oath_readback
from apps.record_chain_intake_gateway.gateway.security import normalize_oath_text, sha256_text


def test_redacted_readback_count_uses_normalized_text():
    raw = "  hello\r\nworld  "
    sub = {"client_oath_readback": {"readback_text": raw}}
    out = redact_transient_oath_readback(sub)
    redacted = out["client_oath_readback"]
    normalized = normalize_oath_text(raw)
    assert redacted["readback_text_sha256"] == sha256_text(normalized)
    assert redacted["readback_text_char_count"] == len(normalized)
    assert "readback_text" not in redacted
