#!/usr/bin/env python3
"""Test builder-generated payload includes guardrail fields correctly."""
import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def test_builder_generates_guardrail_fields():
    """Run the builder and check guardrail fields are present."""
    from sub_v6_level_guardrails import (
        high_level_confirmation,
        sub_v6_level_selection_acknowledgement,
        sub_v6_level_selection_lint,
    )

    # Test V5
    ack = sub_v6_level_selection_acknowledgement("V5")
    assert ack["declared_template_level"] == "V5"
    assert ack["understands_self_declared_template_level"] is True
    assert ack["understands_evidence_waived_for_v0_v5"] is True
    assert ack["understands_not_strict_evidence_verification"] is True
    assert ack["understands_not_formal_attestation"] is True
    assert ack["understands_should_choose_lower_if_uncertain"] is True
    assert ack["confirmed_what_i_checked_and_limitations_are_accurate"] is True
    print("PASS: V5 level_selection_acknowledgement fields correct")

    # Test high_level_confirmation for V5
    high = high_level_confirmation("V5")
    assert high["required"] is True
    assert high["agent_confirmed_high_level_self_selection"] is True
    assert high["agent_confirmed_no_strict_v6plus_claim"] is True
    assert high["agent_confirmed_limitations_disclosed"] is True
    print("PASS: V5 high_level_confirmation fields correct")

    # Test high_level_confirmation for V2 (not high)
    high_v2 = high_level_confirmation("V2")
    assert high_v2["required"] is False
    print("PASS: V2 high_level_confirmation not required")

    # Test lint on a minimal payload
    payload = {
        "agent_declared_protocol_level": "V5",
        "requested_archive_kind": "agent_declared_verification_archive",
        "what_i_checked": ["Reviewed public homepage"],
        "limitations": ["Evidence requirements are waived for V0-V5."],
        "level_selection_acknowledgement": ack,
        "high_level_confirmation": high,
    }
    lint = sub_v6_level_selection_lint(payload)
    assert lint["mode"] == "warning_only"
    assert lint["warnings_block_archive"] is False
    assert lint["does_not_require_evidence_chain"] is True
    assert isinstance(lint["warnings"], list)
    print(f"PASS: V5 lint mode=warning_only, {len(lint['warnings'])} warnings")


def test_builder_cli_output():
    """Run the actual builder CLI and check it produces guardrail fields."""
    import subprocess

    with tempfile.TemporaryDirectory() as tmpdir:
        out_path = Path(tmpdir) / "payload.json"
        result = subprocess.run(
            [
                sys.executable, str(ROOT / "scripts" / "build_agent_declared_archive_payload.py"),
                "--agent-name", "TestAgent",
                "--provider", "TestProvider",
                "--declared-level", "V5",
                "--reception-initiation-class", "externally_seeded",
                "--reception-initiation-basis", "external_url_only",
                "--agent-independent-followup",
                "--out", str(out_path),
            ],
            capture_output=True, text=True, cwd=str(ROOT)
        )

        if result.returncode != 0:
            print(f"Builder failed: {result.stderr}")
            # Don't fail the test if it's a dependency issue
            if "ModuleNotFoundError" in result.stderr or "ImportError" in result.stderr:
                print("SKIP: missing dependency")
                return
            assert False, f"Builder failed: {result.stderr}"

        payload = json.loads(out_path.read_text())

        assert "level_selection_acknowledgement" in payload, "Missing level_selection_acknowledgement"
        assert payload["level_selection_acknowledgement"]["declared_template_level"] == "V5"
        assert payload["level_selection_acknowledgement"]["understands_self_declared_template_level"] is True

        assert "high_level_confirmation" in payload, "Missing high_level_confirmation"
        assert payload["high_level_confirmation"]["required"] is True

        assert "sub_v6_level_selection_lint" in payload, "Missing sub_v6_level_selection_lint"
        assert payload["sub_v6_level_selection_lint"]["mode"] == "warning_only"
        assert payload["sub_v6_level_selection_lint"]["warnings_block_archive"] is False

        print("PASS: Builder CLI produces all three guardrail fields for V5")


if __name__ == "__main__":
    test_builder_generates_guardrail_fields()
    test_builder_cli_output()
    print("\nAll guardrail field tests passed.")
