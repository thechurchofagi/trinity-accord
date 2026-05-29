#!/usr/bin/env python3
"""Run grouped CI test scripts with clear failure reporting."""

import argparse
import subprocess
import sys

DEFAULT_TEST_TIMEOUT_SECONDS = 180
LONG_TEST_TIMEOUT_SECONDS = 600

LONG_RUNNING_COMMAND_KEYWORDS = [
    "test_formal_builder_bundles_default_authorship_smoke.py",
    "test_formal_builder_bundles_are_executable.py",
]


def timeout_for_command(cmd: list[str]) -> int:
    joined = " ".join(cmd)
    for keyword in LONG_RUNNING_COMMAND_KEYWORDS:
        if keyword in joined:
            return LONG_TEST_TIMEOUT_SECONDS
    return DEFAULT_TEST_TIMEOUT_SECONDS


def run_command(cmd: list[str]) -> int:
    timeout = timeout_for_command(cmd)
    print(f"$ {' '.join(cmd)}", flush=True)
    try:
        result = subprocess.run(
            cmd,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        print(
            f"FAIL: command timed out after {timeout}s: {' '.join(cmd)}",
            flush=True,
        )
        return 124

    return result.returncode

GROUPS = {
    "p0-main": [
        # Public surface / sitemap / API metadata
        ["python3", "scripts/check_public_core_consistency.py"],
        ["python3", "scripts/test_mission_governance_contract.py"],
        ["python3", "scripts/test_mission_governance_discovery.py"],
        ["python3", "scripts/test_no_duplicate_context_understanding_system.py"],
        ["python3", "scripts/test_before_leaving_requires_context_governance.py"],
        ["python3", "scripts/test_gateway_routes_context_action_semantics.py"],
        ["python3", "scripts/test_agent_start_no_legacy_c0_c6_context_table.py"],
        ["python3", "scripts/test_closure_report_v30_contract.py"],
        ["python3", "scripts/test_gateway_runtime_contract.py"],
        ["python3", "scripts/test_gateway_error_diagnostics_contract.py"],
        ["python3", "scripts/test_route_selector_contract.py"],
        ["python3", "scripts/test_sitemap_public_sources_exist.py"],
        ["python3", "scripts/test_sitemap_includes_nested_api_json.py"],
        ["python3", "scripts/test_sitemap_permalink_matches_source.py"],
        ["python3", "scripts/test_sitemap_permalink_parser_uses_yaml.py"],
        ["python3", "scripts/test_generate_sitemap_docstring_recursive_api.py"],
        ["python3", "scripts/test_public_referenced_paths_exist.py"],
        ["python3", "scripts/test_public_referenced_paths_core_set.py"],
        ["python3", "scripts/test_public_surface_consistency.py"],
        ["python3", "scripts/test_public_api_sitemap_coverage.py"],
        ["python3", "scripts/test_public_api_metadata_general_not_pass.py"],
        ["python3", "scripts/test_public_api_metadata_tier_b_schema_required.py"],
        ["python3", "scripts/test_public_api_metadata_completeness.py"],
        ["python3", "scripts/test_main_pages_have_machine_counterparts.py"],

        # Context / agent routing
        ["python3", "scripts/test_context_load_map.py"],
        ["python3", "scripts/test_context_pack_inventory_paths.py"],
        ["python3", "scripts/test_agent_start_api.py"],
        ["python3", "scripts/test_agent_start_echo_taxonomy_wording.py"],
        ["python3", "scripts/test_agent_p0_router_contract.py"],
        ["python3", "scripts/test_main_function_route_health.py"],
        ["python3", "scripts/test_e2_verification_echo_not_pure_echo.py"],

        # Route/taxonomy
        ["python3", "scripts/test_gateway_builder_route_map.py"],
        ["python3", "scripts/test_echo_taxonomy_all_consumers_match_single_source.py"],
        ["python3", "scripts/test_no_stale_echo_taxonomy_names.py"],
        ["python3", "scripts/test_echo_type_enum_alignment.py"],
        ["python3", "scripts/test_external_agent_copy_paste_examples_contract.py"],
        ["python3", "scripts/test_external_agent_three_core_builders_source_smoke.py"],
        ["python3", "scripts/test_agent_submit_gateway_echo_types_canonical.py"],
        ["python3", "scripts/test_agent_first_contact_echo_types_canonical.py"],
        ["python3", "scripts/test_agent_facing_pure_echo_routes_canonical.py"],
        ["python3", "scripts/test_gateway_workflows_echo_types_canonical.py"],
        ["python3", "scripts/test_links_expose_first_contact_entrypoints.py"],
        ["python3", "scripts/test_first_contact_text_no_stale_route_guidance.py"],
        ["python3", "scripts/test_agent_exit_readback_policy.py"],
        ["python3", "scripts/test_v30_final_index_contract.py"],
        ["python3", "scripts/test_v30_final_closure_report_contract.py"],
        ["python3", "scripts/test_changelog_v30_5_contract.py"],
        ["python3", "scripts/test_public_api_source_digest_if_present.py"],
        ["python3", "scripts/test_gateway_workflows_echo_types_canonical.py"],
        ["python3", "scripts/test_write_workflows_no_fail_open_rebase.py"],
        ["python3", "scripts/test_workflow_warning_allowlist.py"],
        ["python3", "scripts/test_echo_triage_rate_classifier_ambiguity_guards.py"],

        # Gateway workflow builder contract (v11)
        ["python3", "scripts/test_builder_readback_file_aliases.py"],
        ["python3", "scripts/test_gateway_workflow_builder_cli_contract.py"],
        ["python3", "scripts/test_gateway_workflows_readback_contract.py"],
        ["python3", "scripts/test_gateway_workflow_human_cli_contract.py"],
        ["python3", "scripts/test_gateway_workflows_correction_scope_wording.py"],

        # Post-submit readback contract (v12)
        ["python3", "scripts/test_gateway_workflows_post_submit_readback_contract.py"],
        ["python3", "scripts/test_submit_success_does_not_equal_archived_wording.py"],
        ["python3", "scripts/test_agent_task_router_submit_echo_reads_workflow_manual.py"],
        ["python3", "scripts/test_agent_first_contact_echo_reads_workflow_manual.py"],

        # Guardian workflow & final checklist (v13)
        ["python3", "scripts/test_guardian_listing_stage2_workflow_cli_contract.py"],
        ["python3", "scripts/test_guardian_signed_echo_workflow_wording.py"],
        ["python3", "scripts/test_gateway_workflows_final_checklist_post_submit.py"],
        ["python3", "scripts/test_gateway_workflow_tables_are_contiguous.py"],

        # Non-echo route workflow contract (v14)
        ["python3", "scripts/test_guardian_stage1_workflow_cli_contract.py"],
        ["python3", "scripts/test_gateway_workflows_stage1_inputs_contract.py"],
        ["python3", "scripts/test_first_contact_guardian_reads_workflow_manual.py"],
        ["python3", "scripts/test_first_contact_guardian_stage1_cli_contract.py"],
        ["python3", "scripts/test_first_contact_guardian_stage2_uses_cli_flags.py"],
        ["python3", "scripts/test_first_contact_verification_routes_read_workflow_manual.py"],
        ["python3", "scripts/test_no_stale_or_invented_echo_payload_fields.py"],
        ["python3", "scripts/test_first_contact_forces_copy_paste_or_route_selector.py"],
        ["python3", "scripts/test_runtime_and_route_selector_forbid_invented_values.py"],
        ["python3", "scripts/test_task_router_guardian_reads_workflow_manual.py"],

        # Discovery entrypoint contract (v15)
        ["python3", "scripts/test_well_known_exposes_agent_first_contact_contract.py"],
        ["python3", "scripts/test_links_expose_gateway_workflow_contract.py"],
        ["python3", "scripts/test_discovery_entrypoints_cover_full_agent_journey.py"],

        # Live discovery smoke guards (v16)
        ["python3", "scripts/test_site_live_discovery_smoke_workflow.py"],
        ["python3", "scripts/test_gateway_online_smoke_scope_is_clear.py"],

        # Pages deploy discovery guards (v17)
        ["python3", "scripts/test_deploy_pages_workflow_contract.py"],
        ["python3", "scripts/test_pages_build_contains_agent_discovery.py"],

        # Pages custom domain / live smoke guards (v18)
        ["python3", "scripts/test_pages_custom_domain_contract.py"],

        # Pages live cache diagnostics & action allowlist (v19)
        ["python3", "scripts/test_live_discovery_smoke_cache_diagnostics.py"],
        ["python3", "scripts/test_pages_diagnose_cache_busted.py"],
        ["python3", "scripts/test_deploy_pages_action_allowlist.py"],

        # External agent journey swarm smoke guards (v21)
        ["python3", "scripts/test_external_agent_journey_swarm_smoke_contract.py"],
        ["python3", "scripts/test_site_agent_journey_swarm_workflow.py"],

        # External heterogeneous entrypoint journey smoke guards (v22)
        ["python3", "scripts/test_external_agent_entrypoint_journey_smoke_contract.py"],
        ["python3", "scripts/test_site_agent_entrypoint_journey_workflow.py"],

        # External write lifecycle canary guards (v24 zero-manual)
        ["python3", "scripts/test_external_write_lifecycle_canary_contract.py"],
        ["python3", "scripts/test_site_agent_write_lifecycle_canary_workflow.py"],
        ["python3", "scripts/test_live_canary_policy_contract.py"],
        ["python3", "scripts/test_gateway_discovery_for_canary.py"],
        ["python3", "scripts/test_no_stale_gateway_submit_endpoint.py"],
        ["python3", "scripts/test_external_agent_docs_zero_clone_alignment.py"],
        ["python3", "scripts/test_external_agent_docs_core_routes_clarity.py"],
        ["python3", "scripts/test_external_agent_examples_match_live_smokes.py"],

        # before_leaving exit/readback contract
        ["python3", "scripts/test_agent_output_policy_before_leaving_exit_contract.py"],

        # Zero-clone builder bundle guards (v28)
        ["python3", "scripts/test_formal_builder_bundles_contract.py"],
        ["python3", "scripts/test_external_agent_operation_examples_contract.py"],
        ["python3", "scripts/test_export_formal_builder_bundles.py"],
        ["python3", "scripts/test_download_helper_covers_all_routes.py"],
        ["python3", "scripts/test_zero_clone_routes_in_first_contact.py"],
        ["python3", "scripts/test_zero_clone_docs_cover_all_agent_types.py"],
        ["python3", "scripts/test_gateway_workflows_zero_clone_examples.py"],

        # Zero-clone hardening (v28.1)
        ["python3", "scripts/test_formal_builder_bundle_api_matches_manifests.py"],

        # Zero-clone hardening (v28.2)
        ["python3", "scripts/test_formal_builder_bundle_dependency_closure.py"],
        ["python3", "scripts/test_formal_builder_bundles_are_executable.py"],
        ["python3", "scripts/test_formal_builder_bundles_default_authorship_smoke.py"],

        # CI hardening (v28.3)
        ["python3", "scripts/test_deploy_pages_workflow_contract_is_static.py"],
        ["python3", "scripts/test_run_ci_group_timeouts.py"],

        # v29 homepage zero-clone paths
        ["python3", "scripts/test_homepage_exposes_zero_clone_agent_paths.py"],

        # v29 signed builder bundle manifests
        ["python3", "scripts/test_formal_builder_bundle_signature_contract.py"],
        ["python3", "scripts/verify_formal_builder_bundle_signatures.py"],

        # v29 before_leaving schema
        ["python3", "scripts/test_agent_before_leaving_report_schema.py"],

        # v29 concurrent preflight swarm contract
        ["python3", "scripts/test_concurrent_preflight_swarm_contract.py"],

        # v29 agent live-health
        ["python3", "scripts/test_agent_live_health_contract.py"],

        # Gateway / Guardian core
        ["python3", "scripts/test_gateway_endpoint_contracts.py"],
        ["python3", "scripts/test_gateway_payload_semantic_validator.py"],
        ["python3", "scripts/test_gateway_intake_guardian_fields.py"],
        ["python3", "scripts/test_archive_echo_issue_gateway_intake_strict.py"],
        ["python3", "scripts/test_gateway_auto_archive_uses_shared_eligibility.py"],
        ["python3", "scripts/test_guardian_auto_register_uses_shared_intake.py"],
        ["python3", "scripts/test_guardian_auto_register_intake_strictness.py"],
        ["python3", "scripts/test_guardian_auto_register_listing_e6_behavior.py"],
        ["python3", "scripts/test_guardian_listing_kind_cutoff.py"],
        ["python3", "scripts/test_guardian_listing_body_fallback_cutoff.py"],

        # Generated drift
        ["python3", "scripts/check_verification_index_urllib.py", "--repo", "thechurchofagi/trinity-accord"],
        ["python3", "scripts/generate_public_home_status.py", "--check"],
        ["python3", "scripts/test_home_public_status_sync.py"],

        # v30.3 authorship closure
        ["python3", "scripts/test_zero_clone_authorship_dependency_closure.py"],
        ["python3", "scripts/test_authorship_helpers_are_cwd_independent.py"],
        # P0 group guards
        ["python3", "scripts/test_p0_main_required_commands.py"],
        ["python3", "scripts/test_p0_uses_public_core_consistency.py"],
        ["python3", "scripts/test_deep_integrity_includes_pages_build.py"],
        ["python3", "scripts/test_gateway_online_smoke_workflow.py"],
        ["python3", "scripts/test_public_core_consistency_required_links.py"],

        # v30.7 Gateway receipt triage alignment
        ["python3", "scripts/test_gateway_receipt_contract.py"],
        ["python3", "scripts/test_gateway_receipt_verifier.py"],
        ["python3", "scripts/test_triage_accepts_gateway_receipt.py"],
        ["python3", "scripts/test_triage_rejects_forged_gateway_receipt.py"],
        ["python3", "scripts/test_issue_299_gateway_receipt_regression.py"],
        # v30.7.2 receipt triage false-invalid fix
        ["python3", "scripts/test_issue_302_gateway_receipt_regression.py"],
        ["python3", "scripts/test_triage_uses_shared_receipt_verifier.py"],
        # v30.8 Gateway archive persistence
        ["python3", "scripts/test_gateway_archive_persistence_contract.py"],
        ["python3", "scripts/test_gateway_archive_issue_reader_issue_304.py"],
        ["python3", "scripts/test_archive_gateway_echo_workflow_contract.py"],
        # Guardian retirement automation
        ["python3", "scripts/test_guardian_retirement_automation.py"],
        ["python3", "scripts/test_render_gateway_issue_body_receipt_marker.py"],
        ["python3", "scripts/test_readback_hash_policy.py"],
    ],
    "guardian": [
        ["python3", "scripts/test_guardian_automated_verification.py"],
        ["python3", "scripts/test_guardian_gateway_integration.py"],
        ["python3", "scripts/test_guardian_status_enum_consistency.py"],
        ["python3", "scripts/test_guardian_registry_numbers.py"],
        ["python3", "scripts/test_guardian_reserved_numbering_policy.py"],
        ["python3", "scripts/test_guardian_active_listing_automation.py"],
        ["python3", "scripts/test_guardian_listing_request_builder.py"],
        ["python3", "scripts/test_guardian_auto_registration_from_gateway_issues.py"],
        ["python3", "scripts/test_guardian_registry_schema_current_shape.py"],
        ["python3", "scripts/test_guardian_00001_public_finalization.py"],
        ["python3", "scripts/test_guardian_key_metadata.py"],
        ["python3", "scripts/test_guardian_stewardship_clarity.py"],
        ["python3", "scripts/test_guardian_canonicalization_parity.py"],
        ["python3", "scripts/test_guardian_proof_builder_roundtrip.py"],
        ["python3", "scripts/test_guardian_joint_application_schema.py"],
        ["python3", "scripts/test_unified_proof_canonicalization.py"],
        ["python3", "scripts/test_dual_proof_roundtrip.py"],
        ["python3", "scripts/test_dual_proof_ordering_policy.py"],
        ["python3", "scripts/test_create_guardian_application_one_shot.py"],
        ["python3", "scripts/test_guardian_application_agent_prompt_clarity.py"],
        ["python3", "scripts/test_guardian_application_gateway_payload_completeness.py"],
        ["python3", "scripts/test_guardian_one_shot_safe_language.py"],
        ["python3", "scripts/test_create_guardian_application_diagnostics.py"],
        ["python3", "scripts/test_guardian_wrong_builder_rejection.py"],
        ["python3", "scripts/test_guardian_one_shot_builder_is_only_supported_path.py"],
        ["python3", "scripts/test_agent_first_contact_guardian_policy.py"],
        ["python3", "scripts/test_guardian_docs_convergence.py"],
        ["python3", "scripts/test_public_home_status_guardian_registry.py"],
        ["python3", "scripts/test_public_home_status_check_is_read_only.py"],
        ["python3", "scripts/test_guardian_daily_cap_policy.py"],
        ["python3", "scripts/test_guardian_listing_request_structured_fields.py"],
        ["python3", "scripts/test_guardian_wrong_builder_reroute.py"],
        ["python3", "scripts/test_guardian_listing_payload_profile.py"],
        ["python3", "scripts/test_diagnose_guardian_listing_payload.py"],
        ["python3", "scripts/test_guardian_workflow_rebase_retry_and_comment_upsert.py"],
        ["python3", "scripts/test_guardian_workflow_dispatch_authorization.py"],
        ["python3", "scripts/test_guardian_listing_payload_schema_acceptance.py"],

        ["python3", "scripts/test_guardian_authorship_canonical_contract.py"],
        ["python3", "scripts/test_guardian_listing_gateway_handshake.py"],

        ["python3", "scripts/test_guardian_authorship_digest_self_check.py"],
        ["python3", "scripts/test_guardian_preflight_preserves_error_body.py"],
        ["python3", "scripts/test_guardian_preflight_fingerprint_headers.py"],
        ["python3", "scripts/test_guardian_listing_debug_bundle.py"],

        ["python3", "scripts/test_verification_oath_v2.py"],
        ["python3", "scripts/test_guardian_application_oath_and_identity.py"],
        ["python3", "scripts/test_guardian_listing_oath_and_identity.py"],
        ["python3", "scripts/test_guardian_daily_cap_config.py"],
        ["python3", "scripts/test_guardian_auto_registration_identity_mismatch.py"],
        ["python3", "scripts/test_gateway_render_oath_identity_fields.py"],
        ["python3", "scripts/test_guardian_listing_renderer_excludes_reception_total.py"],
        ["python3", "scripts/test_echo_archive_renderer_counts_reception.py"],
        ["python3", "scripts/test_oath_contract_validator.py"],

        ["python3", "scripts/test_guardian_listing_builder_no_null_intake_fields.py"],
        ["python3", "scripts/test_gateway_render_no_null_identity_intake_fields.py"],
        ["node", "examples/github-app-backend/test-placeholder-detector.mjs"],
        ["python3", "scripts/test_guardian_oath_readback_sha.py"],
        ["python3", "scripts/test_guardian_body_fallback_missing_timestamp_policy.py"],

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
    "verification-index": [
        ["python3", "scripts/build_agent_declared_verification_index_from_issues.py", "--repo", "thechurchofagi/trinity-accord", "--check"],
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
    "readback-integrity": [
        ["python3", "scripts/test_oath_readback_integrity.py"],
        ["python3", "scripts/test_agent_declared_builder_readback_sha.py"],
        ["python3", "scripts/test_agent_declared_echo_builder_readback_sha.py"],
        ["python3", "scripts/test_all_verification_oath_builders_have_readback_sha.py"],
        ["python3", "scripts/test_gateway_payload_readback_sha_validator.py"],
        ["python3", "scripts/test_guardian_oath_readback_sha.py"],
        ["node", "examples/github-app-backend/test-readback-integrity.mjs"],
    ],
    "route-correction": [
        ["python3", "scripts/test_gateway_builder_route_map.py"],
        ["python3", "scripts/test_gateway_builder_route_advisor.py"],
        ["python3", "scripts/test_pure_echo_builder_rejects_unproofed_guardian_identity.py"],
        ["python3", "scripts/test_guardian_echo_builder_smoke.py"],
        ["node", "examples/github-app-backend/test-guardian-identity-claim-requires-proof.mjs"],
        ["node", "examples/github-app-backend/test-forbidden-archive-claims-negation.mjs"],
    ],
    "agent-start-docs": [
        ["python3", "scripts/test_agent_start_docs.py"],
        ["python3", "scripts/test_agent_start_api.py"],
        ["node", "examples/github-app-backend/test-gateway-error-recovery-context.mjs"],
    ],
    "gateway-workflows": [
        ["python3", "scripts/test_gateway_workflow_docs.py"],
        ["python3", "scripts/test_gateway_workflow_api.py"],
        ["node", "examples/github-app-backend/test-gateway-error-workflow-context.mjs"],
    ],
    "legacy-regressions": [
        ["python3", "scripts/check_consistency.py"],
    ],
    "pages-build": [
        ["bash", "scripts/test_jekyll_build_smoke.sh"],
    ],
    "fast-regression": [
        ["python3", "scripts/test_blocker1_v4_default_archive_kind.py"],
        ["python3", "scripts/test_oath_strictness_consistency.py"],
        ["python3", "scripts/test_v0_v5_entrypoint_consistency.py"],
    ],
    "live-site": [
        ["python3", "scripts/smoke_live_zero_clone_builder_bundles.py", "--site", "https://www.trinityaccord.org"],
        ["python3", "scripts/smoke_external_agent_entrypoint_journeys.py", "--site", "https://www.trinityaccord.org"],
        ["python3", "scripts/diagnose_live_propagation.py"],
    ],
    "live-site-swarm": [
        ["python3", "scripts/smoke_external_agent_concurrent_preflight_swarm.py", "--agents", "20", "--workers", "8", "--max-failures", "20"],
    ],
    "live-site-gateway-core": [
        ["python3", "scripts/smoke_live_external_agent_three_core_preflight.py"],
        ["python3", "scripts/smoke_live_zero_clone_authorship_closure.py"],
    ],
    "live-site-gateway-receipt": [
        ["python3", "scripts/smoke_live_gateway_receipt_triage_alignment.py"],
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
        rc = run_command(cmd)
        print("::endgroup::", flush=True)
        if rc != 0:
            failures.append((cmd, rc))
            break

    if failures:
        for cmd, code in failures:
            print(f"FAILED ({code}): {' '.join(cmd)}", file=sys.stderr)
        raise SystemExit(1)

    marker = args.group.upper().replace("-", "_")
    print(f"CI_GROUP_{marker}_OK")




if __name__ == "__main__":
    main()
