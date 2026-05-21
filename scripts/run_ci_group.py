#!/usr/bin/env python3
"""Run grouped CI test scripts with clear failure reporting."""

import argparse
import subprocess
import sys

GROUPS = {
    "guardian": [
        ["python3", "scripts/test_guardian_automated_verification.py"],
        ["python3", "scripts/test_guardian_gateway_integration.py"],
        ["python3", "scripts/test_guardian_status_enum_consistency.py"],
        ["python3", "scripts/test_guardian_registry_numbers.py"],
        ["python3", "scripts/test_guardian_key_metadata.py"],
        ["python3", "scripts/test_guardian_stewardship_clarity.py"],
        ["python3", "scripts/test_guardian_canonicalization_parity.py"],
        ["python3", "scripts/test_guardian_proof_builder_roundtrip.py"],
        ["python3", "scripts/test_guardian_joint_application_schema.py"],
        ["python3", "scripts/test_unified_proof_canonicalization.py"],
        ["python3", "scripts/test_dual_proof_roundtrip.py"],
        ["python3", "scripts/test_dual_proof_ordering_policy.py"],

    ],
    "chronicle": [
        ["python3", "scripts/generate_nft_chronicle_context.py"],
        ["python3", "scripts/test_nft_chronicle_context_artifacts.py"],
        ["python3", "scripts/generate_chronicle_music_canonical.py"],
        ["git", "diff", "--exit-code", "nft-text-descriptions/chronicle-music-canonical.json"],
        ["python3", "scripts/test_chronicle_site_integration.py"],
    ],
    "supply-chain": [
        ["python3", "scripts/test_action_pinning.py"],
        ["python3", "scripts/test_runner_image_pinning.py"],
        ["python3", "scripts/test_python_dependency_pinning.py"],
        ["python3", "scripts/test_node_dependency_pinning.py"],
        ["python3", "scripts/test_toolchain_provenance.py"],
        ["python3", "scripts/test_write_workflow_toolchain_provenance.py"],
        ["python3", "scripts/test_no_remote_script_execution.py"],
        ["python3", "scripts/test_system_tool_version_recording.py"],
    ],
    "echo-archive": [
        ["python3", "scripts/test_echo_human_review_archive_authorization.py"],
        ["python3", "scripts/test_echo_archive_toctou_digest.py"],
        ["python3", "scripts/test_echo_screened_digest_trusted_comment_source.py"],
        ["python3", "scripts/test_echo_archive_markdown_escape.py"],
        ["python3", "scripts/test_echo_archive_verification_level_metadata.py"],
        ["python3", "scripts/test_echo_untrusted_content_marking.py"],
    ],
    "claim-gate": [
        ["python3", "scripts/test_claim_gate_high_level_hard_gates.py"],
        ["python3", "scripts/test_claim_gate_authority_boundary_foundation.py"],
        ["python3", "scripts/test_evidence_schema_high_level_constraints.py"],
        ["python3", "scripts/test_v8_semantics_consistency.py"],
        ["python3", "scripts/test_claim_gate_v5_v6_v7_profiles.py"],
        ["python3", "scripts/test_claim_gate_v4plus_v5_boundaries.py"],
        ["python3", "scripts/test_claim_gate_v8_requires_core_baseline.py"],
        ["python3", "scripts/test_claim_gate_high_component_does_not_raise_protocol.py"],
        ["python3", "scripts/test_claim_gate_t8_uncertainty_strict.py"],
        ["python3", "scripts/test_claim_gate_p7_p8_external_report_requirements.py"],
    ],
    "trust-root": [
        ["python3", "scripts/validate_authority_manifest.py", "--self-test"],
        ["python3", "scripts/validate_authority_manifest.py", "archive/authority-manifest/authority.jcs.json"],
        ["python3", "scripts/validate_btc_signature_manifest.py", "--self-test"],
        ["python3", "scripts/validate_btc_signature_manifest.py", "archive/btc-signature/btc-signature.json"],
        ["python3", "scripts/validate_eth_witness_manifest.py", "--self-test"],
        ["python3", "scripts/validate_eth_witness_manifest.py", "archive/eth-witness/eth-witness.json"],
        ["python3", "scripts/validate_trust_root_policy.py", "--self-test"],
        ["python3", "scripts/validate_trust_root_policy.py", "archive/trust-root-policy.json"],
        ["python3", "scripts/test_trust_root_cross_checks.py"],
    ],
}


def main():
    parser = argparse.ArgumentParser(description="Run grouped CI test scripts")
    parser.add_argument("group", choices=sorted(GROUPS), help="Test group to run")
    parser.add_argument("--list", action="store_true", help="List available groups")
    args = parser.parse_args()

    if args.list:
        for name, cmds in sorted(GROUPS.items()):
            print(f"  {name}: {len(cmds)} tests")
        return

    failures = []
    for cmd in GROUPS[args.group]:
        print(f"::group::{args.group}: {' '.join(cmd)}", flush=True)
        result = subprocess.run(cmd)
        print("::endgroup::", flush=True)
        if result.returncode != 0:
            failures.append((cmd, result.returncode))
            break

    if failures:
        for cmd, code in failures:
            print(f"FAILED ({code}): {' '.join(cmd)}", file=sys.stderr)
        raise SystemExit(1)

    marker = args.group.upper().replace("-", "_")
    print(f"CI_GROUP_{marker}_OK")


if __name__ == "__main__":
    main()
