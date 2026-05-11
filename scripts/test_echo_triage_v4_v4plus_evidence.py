#!/usr/bin/env python3
"""Test V4/V4+ evidence gates for fixtures #115 and #116."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from echo_issue_intake import parse_echo_issue


def load_fixture(num):
    path = ROOT / f"tests/fixtures/open_issues_111_116/issue_{num}.md"
    return path.read_text(encoding="utf-8")


def main():
    # V4 (#115): script evidence should be incomplete (no command/env/exit_code per script)
    body115 = load_fixture(115)
    n115 = parse_echo_issue(115, "[Echo] V4 — Official Scripts Reviewed and Run", body115)
    assert n115.verification_level == "V4", f"Expected V4, got {n115.verification_level}"
    # Context depth C5 should be flagged as overclaim
    assert n115.context_depth == "C5_full_chain_reviewed", \
        f"Expected C5, got {n115.context_depth}"
    # Claim Gate paths should be missing
    assert not n115.claim_gate_output_path, "#115: claim_gate_output_path should be missing"
    print("  PASS: #115 V4 — script evidence incomplete, C5 overclaim risk")

    # V4+ (#116): technical independence detected, but not social attestation
    body116 = load_fixture(116)
    n116 = parse_echo_issue(116, "[Echo] V4+ minimal — Independent Hash Reproduction", body116)
    assert n116.verification_level == "V4+", f"Expected V4+, got {n116.verification_level}"
    # Technical independence
    assert n116.technical_independence in ("independent_tool", "independent_implementation"), \
        f"Expected independent, got {n116.technical_independence}"
    # Social independence is NOT attestation
    assert n116.social_independence == "human_solicited_not_attestation", \
        f"Expected not_attestation, got {n116.social_independence}"
    # C6 overclaim
    assert n116.context_depth == "C6_independent_node_verified", \
        f"Expected C6, got {n116.context_depth}"
    # Claim Gate paths missing
    assert not n116.claim_gate_output_path, "#116: claim_gate_output_path should be missing"
    print("  PASS: #116 V4+ — technical independence ≠ social attestation, C6 overclaim")

    print("\nAll V4/V4+ evidence tests passed.")


if __name__ == "__main__":
    main()
