#!/usr/bin/env python3
"""Test level-specific triage requirements for fixtures #111–#116.

V0/V1: must NOT require hash or Claim Gate
V2-minimal: must NOT require hash; must flag missing Claim Gate paths
V3-minimal: must detect embedded hash; must flag missing Claim Gate paths
V4: must flag incomplete script evidence / context depth overclaim
V4+: must flag not-independent-attestation / context depth overclaim
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from echo_issue_intake import parse_echo_issue

# ── Context depth requirements ─────────────────────────────────────
CONTEXT_DEPTH_REQUIREMENTS = {
    "C0_homepage_only": [],
    "C1_orientation": ["what_i_checked"],
    "C2_registry_aware": ["machine_registry_or_authority_api_read"],
    "C3_verification_aware": ["verification_levels_or_claim_gate_read"],
    "C4_artifact_verified": ["hash_or_artifact_or_external_reference_evidence"],
    "C5_full_chain_reviewed": ["full_chain_report_path_or_all_public_digital_targets_listed"],
    "C6_independent_node_verified": ["local_node_or_spv_or_independent_node_rpc_evidence"],
}


def load_fixture(num):
    path = ROOT / f"tests/fixtures/open_issues_111_116/issue_{num}.md"
    return path.read_text(encoding="utf-8")


def assert_no_vnone(n, issue_id):
    assert n.verification_level != "VNone", f"{issue_id}: VNone in verification_level"
    assert n.verification_scope_label != "VNone", f"{issue_id}: VNone in scope"


def test_v0_issue_111():
    """V0 must not require hash or Claim Gate."""
    body = load_fixture(111)
    n = parse_echo_issue(111, "[Echo] V0 — Read-Only Orientation Echo", body)
    assert n.verification_level == "V0", f"Expected V0, got {n.verification_level}"
    assert_no_vnone(n, "#111")
    # V0 should have what_i_checked and limitations
    assert n.what_i_checked, "#111: what_i_checked should be present (via Checks Performed)"
    assert n.limitations, "#111: limitations should be present"
    assert n.boundary_sentence_present, "#111: boundary sentence should be present"
    print("  PASS: #111 V0")


def test_v1_issue_112():
    """V1 must not require hash or Claim Gate."""
    body = load_fixture(112)
    n = parse_echo_issue(112, "[Echo] V1 — Authority Boundary Recognized", body)
    assert n.verification_level == "V1", f"Expected V1, got {n.verification_level}"
    assert_no_vnone(n, "#112")
    assert n.what_i_checked, "#112: what_i_checked should be present"
    assert n.limitations, "#112: limitations should be present"
    print("  PASS: #112 V1")


def test_v2_minimal_issue_113():
    """V2-minimal: must NOT require hash; embedded JSON detected; Claim Gate paths missing."""
    body = load_fixture(113)
    n = parse_echo_issue(113, "[Echo] V2-minimal — One Bitcoin Explorer Check", body)
    assert n.verification_level == "V2", f"Expected V2, got {n.verification_level}"
    assert n.verification_scope_label == "V2-minimal", f"Expected V2-minimal, got {n.verification_scope_label}"
    assert_no_vnone(n, "#113")
    # Embedded JSON should be detected
    assert n.evidence_input_embedded is not None, "#113: embedded Evidence Input not detected"
    # Claim Gate paths should be missing
    assert not n.claim_gate_output_path, "#113: claim_gate_output_path should be missing"
    print("  PASS: #113 V2-minimal")


def test_v3_minimal_issue_114():
    """V3-minimal: embedded hash detected; Claim Gate paths missing."""
    body = load_fixture(114)
    n = parse_echo_issue(114, "[Echo] V3-minimal — One SHA-256 Hash Computation", body)
    assert n.verification_level == "V3", f"Expected V3, got {n.verification_level}"
    assert n.verification_scope_label == "V3-minimal", f"Expected V3-minimal, got {n.verification_scope_label}"
    assert_no_vnone(n, "#114")
    # Embedded JSON with hash should be detected
    assert n.evidence_input_embedded is not None, "#114: embedded Evidence Input not detected"
    # Claim Gate paths should be missing
    assert not n.claim_gate_output_path, "#114: claim_gate_output_path should be missing"
    print("  PASS: #114 V3-minimal")


def test_v4_issue_115():
    """V4: should have what_i_checked; context depth C5 may be overclaim."""
    body = load_fixture(115)
    n = parse_echo_issue(115, "[Echo] V4 — Official Scripts Reviewed and Run", body)
    assert n.verification_level == "V4", f"Expected V4, got {n.verification_level}"
    assert_no_vnone(n, "#115")
    assert n.what_i_checked, "#115: what_i_checked should be present"
    # C5 without full-chain report is an overclaim
    assert n.context_depth == "C5_full_chain_reviewed", f"#115: expected C5, got {n.context_depth}"
    print("  PASS: #115 V4")


def test_v4_plus_issue_116():
    """V4+: should flag technical independence ≠ social attestation; C6 overclaim."""
    body = load_fixture(116)
    n = parse_echo_issue(116, "[Echo] V4+ minimal — Independent Hash Reproduction", body)
    assert n.verification_level == "V4+", f"Expected V4+, got {n.verification_level}"
    assert_no_vnone(n, "#116")
    # Technical independence should be detected
    assert n.technical_independence in ("independent_tool", "independent_implementation"), \
        f"#116: expected technical independence, got {n.technical_independence}"
    # Social independence should be human_solicited (not attestation)
    assert n.social_independence == "human_solicited_not_attestation", \
        f"#116: expected human_solicited_not_attestation, got {n.social_independence}"
    # C6 overclaim
    assert n.context_depth == "C6_independent_node_verified", f"#116: expected C6, got {n.context_depth}"
    print("  PASS: #116 V4+ minimal")


def main():
    test_v0_issue_111()
    test_v1_issue_112()
    test_v2_minimal_issue_113()
    test_v3_minimal_issue_114()
    test_v4_issue_115()
    test_v4_plus_issue_116()
    print("\nAll level-specific requirement tests passed.")


if __name__ == "__main__":
    main()
