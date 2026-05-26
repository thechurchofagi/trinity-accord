#!/usr/bin/env python3
"""Test echo_issue_intake.py section aliases and verification level parsing."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from echo_issue_intake import parse_echo_issue


def test_checks_performed_alias():
    """Checks Performed must satisfy what_i_checked."""
    body = """## Echo Submission

**Verification Level:** V0 | **Scope Label:** V0

### Checks Performed
- Read homepage

### What Remains Uncertain
- Everything technical

**Bitcoin Originals are final; all mirrors and echoes are non-amending.**
"""
    n = parse_echo_issue(None, "[Echo] V0", body)
    assert n.what_i_checked, "Checks Performed must satisfy what_i_checked"
    assert "Read homepage" in n.what_i_checked
    assert n.limitations, "What Remains Uncertain should satisfy limitations fallback"
    assert n.boundary_sentence_present is True
    print("  PASS: test_checks_performed_alias")


def test_verification_level_and_scope_parse():
    """Parse V3 / V3-minimal from header line."""
    body = "**Verification Level:** V3 | **Scope Label:** V3-minimal"
    n = parse_echo_issue(None, "[Echo] V3-minimal", body)
    assert n.verification_level == "V3", f"Expected V3, got {n.verification_level}"
    assert n.verification_scope_label == "V3-minimal", f"Expected V3-minimal, got {n.verification_scope_label}"
    print("  PASS: test_verification_level_and_scope_parse")


def test_title_scope_parse_fallback():
    """Parse V2-minimal from title when body has no header."""
    body = "No header."
    n = parse_echo_issue(None, "[Echo] V2-minimal — One Bitcoin Explorer Check", body)
    assert n.verification_level == "V2", f"Expected V2, got {n.verification_level}"
    assert n.verification_scope_label == "V2-minimal", f"Expected V2-minimal, got {n.verification_scope_label}"
    print("  PASS: test_title_scope_parse_fallback")


def test_never_emit_vnone():
    """Parser must never return VNone."""
    body = "No verification info at all."
    n = parse_echo_issue(None, "[Echo] Test", body)
    assert n.verification_level != "VNone", "Parser returned VNone"
    assert n.verification_scope_label != "VNone", "Parser returned VNone scope"
    print("  PASS: test_never_emit_vnone")


def test_v4_plus_parse():
    """Parse V4+ correctly."""
    body = "**Verification Level:** V4+ | **Scope Label:** V4+ minimal"
    n = parse_echo_issue(None, "[Echo] V4+ minimal", body)
    assert n.verification_level == "V4+", f"Expected V4+, got {n.verification_level}"
    assert n.verification_scope_label == "V4+ minimal", f"Expected 'V4+ minimal', got {n.verification_scope_label}"
    print("  PASS: test_v4_plus_parse")


def test_boundary_sentence_detection():
    """Detect exact boundary sentence."""
    body1 = "Bitcoin Originals are final; all mirrors and echoes are non-amending."
    n1 = parse_echo_issue(None, "[Echo] V0", body1)
    assert n1.boundary_sentence_present is True

    body2 = "No boundary here."
    n2 = parse_echo_issue(None, "[Echo] V0", body2)
    assert n2.boundary_sentence_present is False
    print("  PASS: test_boundary_sentence_detection")


def test_embedded_json_detection():
    """Detect embedded Evidence Input JSON."""
    body = """
### Evidence Input (JSON)
```json
{
  "schema": "trinityaccord.evidence-input.v1",
  "evidence": {"hashes": [{"match": true}]},
  "claims_requested_by_agent": ["V3"]
}
```
"""
    n = parse_echo_issue(None, "[Echo] V3", body)
    assert n.evidence_input_embedded is not None, "Embedded JSON not detected"
    assert n.evidence_input_embedded.get("schema") == "trinityaccord.evidence-input.v1"
    print("  PASS: test_embedded_json_detection")


def test_context_depth_detection():
    """Detect context depth from body."""
    body = "- **Context Depth:** C4_artifact_verified"
    n = parse_echo_issue(None, "[Echo] V3", body)
    assert n.context_depth == "C4_artifact_verified", f"Got {n.context_depth}"
    print("  PASS: test_context_depth_detection")


def test_integrity_declaration_detection():
    """Detect solemn integrity declaration."""
    body = "### Solemn Integrity Declaration\nI solemnly declare that..."
    n = parse_echo_issue(None, "[Echo] V0", body)
    assert n.integrity_declaration_present is True
    print("  PASS: test_integrity_declaration_detection")


def main():
    test_checks_performed_alias()
    test_verification_level_and_scope_parse()
    test_title_scope_parse_fallback()
    test_never_emit_vnone()
    test_v4_plus_parse()
    test_boundary_sentence_detection()
    test_embedded_json_detection()
    test_context_depth_detection()
    test_integrity_declaration_detection()
    print("\nAll intake alias tests passed.")


if __name__ == "__main__":
    main()
