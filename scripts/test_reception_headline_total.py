#!/usr/bin/env python3
"""Regression test: Reception headline total must sum only mutually exclusive
top-level archived record pools, not classification buckets.

Classification buckets (human_directed_agent_verification, self_initiated_agent_reception,
agent_referred_reception, multi_agent_reception) overlap with archived_echoes
and must NOT be added to the headline total.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from generate_public_home_status import render_block


def test_reception_headline_no_double_count():
    """Reception headline = archived_echoes + agent_declared_verification_archives
    + agent_declared_attestations + agent_declared_successor_receptions ONLY."""
    status = {
        "verifiability": {
            "bitcoin_originals": {"present": True, "canonical_authority": True},
            "public_digital_verification": {
                "highest_protocol_level": "V4",
                "highest_component_context": "D2",
                "claim_gate_required": True,
                "claim_gate_modes": {"V0_to_V5": "template_for_v0_v5", "V6_to_V8": "strict_evidence"},
                "highest_level_basis": "agent_declared_template_pass",
                "agent_declared_highest_protocol_level": "V4",
                "evidence_requirement_mode_for_highest": "waived_for_v0_v5"
            },
            "physical_anchor_context": {"highest_public_context": "P3", "does_not_auto_raise_protocol_level": True}
        },
        "reception": {
            "archived_echoes": {"count": 3},
            "agent_declared_verification_archives": {"count": 1, "highest_level": "V4"},
            "agent_declared_attestations": {"count": 0},
            "agent_declared_successor_receptions": {"count": 0},
            # These are classification buckets — must NOT inflate headline
            "human_directed_agent_verification": {"count": 1, "highest_level": "V3"},
            "agent_referred_reception": {"count": 5, "highest_reception_class": "none"},
            "agent_referred_verification": {"count": 2, "highest_level": "none"},
            "self_initiated_agent_reception": {"count": 1, "highest_reception_class": "none"},
            "self_initiated_agent_verification": {"count": 0, "highest_level": "none"},
            "multi_agent_reception": {"count": 7, "highest_reception_class": "none"},
            "successor_civilization_reception": {"claimed": False, "highest_reception_class": "none"}
        },
        "external_witness_records": {
            "notarial_or_legal_provenance": {"count": 0},
            "institutional_or_audit_reports": {"count": 0}
        },
        "boundary": {"preserved": True},
        "source_digest": "test123"
    }

    html = render_block(status)

    # Expected: 3 + 1 + 0 + 0 = 4 (NOT 3+1+1+5+7=17)
    assert '<p class="status-number">4</p>' in html, \
        f"Expected Reception=4, got:\n{html}"

    # Ensure classification bucket counts do NOT appear as headline
    assert '<p class="status-number">17</p>' not in html, \
        "Classification buckets must not inflate headline Reception total"
    assert '<p class="status-number">6</p>' not in html, \
        "Old double-counted total must not appear"

    print("PASS: reception_headline_no_double_count")
    return True


if __name__ == "__main__":
    ok = test_reception_headline_no_double_count()
    sys.exit(0 if ok else 1)
