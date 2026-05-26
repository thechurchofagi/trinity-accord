#!/usr/bin/env python3
"""Test that warning-only lint emits warnings but does not block."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sub_v6_level_guardrails import collect_sub_v6_level_selection_warnings


def test_v5_thin_what_checked():
    """V5 with thin what_i_checked should produce a warning."""
    payload = {
        "agent_declared_protocol_level": "V5",
        "requested_archive_kind": "agent_declared_verification_archive",
        "what_i_checked": ["Read public homepage"],
        "limitations": ["Evidence requirements are waived for V0-V5."],
    }
    warnings = collect_sub_v6_level_selection_warnings(payload)
    assert len(warnings) > 0, "V5 with thin what_i_checked should produce warnings"
    assert any("high sub-V6" in w.lower() or "script" in w.lower() for w in warnings)
    print(f"PASS: V5 thin what_i_checked produces {len(warnings)} warnings")


def test_v4_no_script_mention():
    """V4 without script mention should warn."""
    payload = {
        "agent_declared_protocol_level": "V4",
        "requested_archive_kind": "agent_declared_verification_archive",
        "what_i_checked": ["Read documentation"],
        "limitations": [],
    }
    warnings = collect_sub_v6_level_selection_warnings(payload)
    assert len(warnings) > 0, "V4 without script mention should warn"
    print(f"PASS: V4 no script mention produces {len(warnings)} warnings")


def test_v3_limitation_no_hash():
    """V3 with limitation 'did not compute hash' should warn."""
    payload = {
        "agent_declared_protocol_level": "V3",
        "requested_archive_kind": "agent_declared_verification_archive",
        "what_i_checked": ["Read documentation"],
        "limitations": ["Did not compute hash"],
    }
    warnings = collect_sub_v6_level_selection_warnings(payload)
    assert any("hash" in w.lower() for w in warnings), "Should warn about missing hash"
    print(f"PASS: V3 'did not compute hash' produces warning")


def test_v2_no_warning():
    """V2 with basic checks should not produce level-specific warnings."""
    payload = {
        "agent_declared_protocol_level": "V2",
        "requested_archive_kind": "agent_declared_verification_archive",
        "what_i_checked": ["Read public homepage", "Checked external reference"],
        "limitations": ["Evidence requirements are waived for V0-V5."],
    }
    warnings = collect_sub_v6_level_selection_warnings(payload)
    # V2 is not high sub-V6, so no script/hash warnings expected
    level_warnings = [w for w in warnings if "high sub-V6" in w.lower() or "V3+" in w]
    assert not level_warnings, f"V2 should not trigger high-level warnings: {level_warnings}"
    print("PASS: V2 does not trigger high-level warnings")


def test_non_verification_no_warning():
    """Non-verification archive should not trigger warnings."""
    payload = {
        "agent_declared_protocol_level": "V5",
        "requested_archive_kind": "agent_declared_echo_archive",
        "what_i_checked": ["Read"],
        "limitations": [],
    }
    warnings = collect_sub_v6_level_selection_warnings(payload)
    assert warnings == [], "Non-verification archive should not trigger warnings"
    print("PASS: Non-verification archive produces no warnings")


if __name__ == "__main__":
    test_v5_thin_what_checked()
    test_v4_no_script_mention()
    test_v3_limitation_no_hash()
    test_v2_no_warning()
    test_non_verification_no_warning()
    print("\nAll warning-only lint tests passed.")
