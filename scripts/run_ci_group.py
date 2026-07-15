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
    "p0-current": [
        # --- Record-chain-first current主线硬门禁 ---
        # Public surface / sitemap / API metadata
        ["python3", "scripts/check_public_core_consistency.py"],
        ["python3", "scripts/check_active_public_routes.py"],
        ["python3", "scripts/test_mission_governance_contract.py"],
        ["python3", "scripts/test_mission_governance_discovery.py"],
        ["python3", "scripts/test_mission_public_route_parity.py"],
        ["python3", "scripts/test_builder_help_urls_resolve.py"],
        ["python3", "scripts/test_autonomy_inventory_boundary.py"],
        ["python3", "scripts/test_gateway_runtime_recovery_links.py"],
        ["python3", "scripts/test_gateway_schema_shadow_parity.py"],
        ["python3", "scripts/test_reserved_internal_builder_contract.py"],
        ["python3", "scripts/test_record_chain_intake_gateway_contract.py"],
        ["python3", "scripts/test_no_duplicate_context_understanding_system.py"],
        ["python3", "scripts/test_before_leaving_requires_context_governance.py"],
        ["python3", "scripts/test_agent_start_no_legacy_c0_c6_context_table.py"],
        ["python3", "scripts/test_closure_report_v30_contract.py"],
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

        # Context / agent routing (current)
        ["python3", "scripts/test_context_load_map.py"],
        ["python3", "scripts/test_context_pack_inventory_paths.py"],
        ["python3", "scripts/test_agent_start_api.py"],
        ["python3", "scripts/test_agent_start_echo_taxonomy_wording.py"],
        ["python3", "scripts/test_agent_p0_router_contract.py"],
        ["python3", "scripts/test_main_function_route_health.py"],
        ["python3", "scripts/test_e2_verification_echo_not_pure_echo.py"],

        # Route/taxonomy (current)
        ["python3", "scripts/test_echo_taxonomy_all_consumers_match_single_source.py"],
        ["python3", "scripts/test_no_stale_echo_taxonomy_names.py"],
        ["python3", "scripts/test_echo_type_enum_alignment.py"],
        ["python3", "scripts/test_external_agent_copy_paste_examples_contract.py"],
        ["python3", "scripts/test_external_agent_three_core_builders_source_smoke.py"],
        ["python3", "scripts/test_agent_first_contact_echo_types_canonical.py"],
        ["python3", "scripts/test_agent_facing_pure_echo_routes_canonical.py"],
        ["python3", "scripts/test_links_expose_first_contact_entrypoints.py"],
        ["python3", "scripts/test_first_contact_text_no_stale_route_guidance.py"],
        ["python3", "scripts/test_agent_exit_readback_policy.py"],
        ["python3", "scripts/test_v30_final_index_contract.py"],
        ["python3", "scripts/test_v30_final_closure_report_contract.py"],
        ["python3", "scripts/test_changelog_v30_5_contract.py"],
        ["python3", "scripts/test_public_api_source_digest_if_present.py"],
        ["python3", "scripts/test_write_workflows_no_fail_open_rebase.py"],
        ["python3", "scripts/test_workflow_warning_allowlist.py"],

        # Discovery entrypoint contract (current)
        ["python3", "scripts/test_well_known_exposes_agent_first_contact_contract.py"],
        ["python3", "scripts/test_discovery_entrypoints_cover_full_agent_journey.py"],

        # Pages deploy discovery guards
        ["python3", "scripts/test_deploy_pages_workflow_contract.py"],
        ["python3", "scripts/test_pages_build_contains_agent_discovery.py"],
        ["python3", "scripts/test_pages_custom_domain_contract.py"],
        ["python3", "scripts/test_deploy_pages_action_allowlist.py"],
        ["python3", "scripts/test_pages_verification_comment_permissions.py"],
        ["python3", "scripts/test_deploy_pages_workflow_contract_is_static.py"],

        # External agent journey smoke guards
        ["python3", "scripts/test_external_agent_journey_swarm_smoke_contract.py"],
        ["python3", "scripts/test_external_agent_entrypoint_journey_smoke_contract.py"],
        ["python3", "scripts/test_external_write_lifecycle_canary_contract.py"],
        ["python3", "scripts/test_live_canary_policy_contract.py"],
        ["python3", "scripts/test_external_agent_docs_zero_clone_alignment.py"],
        ["python3", "scripts/test_external_agent_docs_core_routes_clarity.py"],
        ["python3", "scripts/test_external_agent_examples_match_live_smokes.py"],
        ["python3", "scripts/test_external_agent_operation_examples_contract.py"],

        # before_leaving exit/readback contract
        ["python3", "scripts/test_agent_output_policy_before_leaving_exit_contract.py"],

        # Zero-clone builder bundle guards (current)
        ["python3", "scripts/test_formal_builder_bundles_contract.py"],
        ["python3", "scripts/test_export_formal_builder_bundles.py"],
        ["python3", "scripts/test_download_helper_covers_all_routes.py"],
        ["python3", "scripts/test_zero_clone_routes_in_first_contact.py"],
        ["python3", "scripts/test_zero_clone_docs_cover_all_agent_types.py"],
        ["python3", "scripts/test_formal_builder_bundle_api_matches_manifests.py"],
        ["python3", "scripts/test_formal_builder_bundle_dependency_closure.py"],
        ["python3", "scripts/test_formal_builder_bundles_are_executable.py"],
        ["python3", "scripts/test_formal_builder_bundles_default_authorship_smoke.py"],
        ["python3", "scripts/test_formal_builder_bundle_signature_contract.py"],
        ["python3", "scripts/verify_formal_builder_bundle_signatures.py"],

        # CI hardening
        ["python3", "scripts/test_run_ci_group_timeouts.py"],
        ["python3", "scripts/test_p0_main_required_commands.py"],
        ["python3", "scripts/test_p0_uses_public_core_consistency.py"],
        ["python3", "scripts/test_deep_integrity_includes_pages_build.py"],
        ["python3", "scripts/test_record_chain_write_path_guard_contract.py"],
        ["python3", "scripts/test_record_chain_verifier_invariants.py"],
        ["python3", "scripts/test_classification_update_final_binding.py"],
        ["python3", "scripts/test_deep_intake_append_transaction_invariants.py"],
        ["python3", "scripts/test_public_submission_schema_alignment.py"],
        ["python3", "scripts/test_deep_integrity_group_nonempty.py"],
        ["python3", "scripts/test_action_pinning.py"],
        ["python3", "scripts/test_runner_image_pinning.py"],
        ["python3", "scripts/test_python_dependency_pinning.py"],
        ["python3", "scripts/test_node_dependency_pinning.py"],
        ["python3", "scripts/test_toolchain_provenance.py"],
        ["python3", "scripts/test_write_workflow_toolchain_provenance.py"],
        ["python3", "scripts/test_no_remote_script_execution.py"],
        ["python3", "scripts/test_workflow_dispatch_input_safety.py"],
        ["python3", "scripts/test_system_tool_version_recording.py"],
        ["python3", "scripts/test_readback_hash_parity.py"],
        ["python3", "scripts/test_external_agent_full_auto_pipeline_contract.py"],
        ["python3", "scripts/test_external_agent_first_contact_rules_contract.py"],
        ["python3", "scripts/test_homepage_status_sync_contract.py"],
        ["python3", "scripts/test_waiting_heartbeat_summary_metrics.py"],
        ["python3", "scripts/test_waiting_heartbeat_homepage_card_metrics.py"],
        ["python3", "scripts/test_main_write_workflows_safe_push_contract.py"],

        # Pipeline backlog detector
        ["python3", "scripts/detect_record_chain_pipeline_backlog.py"],
        ["python3", "scripts/detect_archive_backlog.py"],
        ["python3", "scripts/test_archive_backlog_detector.py"],
        ["python3", "scripts/test_archive_backlog_repair_contract.py"],
        ["python3", "scripts/test_native_ots_repair_state_machine.py"],
        ["python3", "scripts/test_native_ots_repair_source_contract.py"],

        # Generated drift
        ["python3", "scripts/generate_arweave_wallet_status.py", "--check"],
        ["python3", "scripts/generate_record_chain_status.py", "--check"],
        ["python3", "scripts/check_public_home_status_contract.py"],
        ["python3", "scripts/test_historic_autonomous_agent_reception_contract.py"],
        ["python3", "scripts/test_home_public_status_sync.py"],
        ["python3", "scripts/test_homepage_status_sync_contract.py"],

        # v30.3 authorship closure
        ["python3", "scripts/test_zero_clone_authorship_dependency_closure.py"],
        ["python3", "scripts/test_authorship_helpers_are_cwd_independent.py"],
        ["python3", "scripts/test_public_core_consistency_required_links.py"],

        # Phase 6B security hotfix (current)
        ["python3", "scripts/test_no_secret_material_committed.py"],
        ["python3", "scripts/test_no_private_key_material_committed.py"],
        ["python3", "scripts/test_phase6b_hotfix.py"],
        ["python3", "scripts/test_phase_6b_hotfix_contract.py"],
        ["python3", "scripts/test_render_deploy_boundary_contract.py"],
        ["python3", "scripts/test_legacy_isolation_contract.py"],
        ["python3", "scripts/test_public_wording_phase6_contract.py"],
        ["node", "downloads/test-record-chain-builder.mjs"],
        ["python3", "scripts/test_builder_classification_target_id.py"],

        # Phase 6B test registry contract
        ["python3", "scripts/test_phase6b_test_registry_contract.py"],

        # Phase 6C: operator secret names, Arweave live readiness, Render manual deploy
        ["python3", "scripts/test_operator_secret_names_contract.py"],
        ["python3", "scripts/test_arweave_live_readiness_contract.py"],
        ["python3", "scripts/test_paid_echo_workflow_contract.py"],
        ["python3", "scripts/test_arweave_upload_contract.py"],
        ["python3", "scripts/test_arweave_upload_wallet_ledger_integration.py"],
        ["python3", "scripts/test_arweave_paid_upload_wallet_wiring.py"],
        ["python3", "scripts/test_render_manual_deploy_contract.py"],

        # Phase 6 scheduled OTS watch
        ["python3", "scripts/test_phase6_ots_watch_workflow_contract.py"],
        ["python3", "scripts/test_ots_pending_detection.py"],

        # Native OTS upgraded/verified lifecycle
        ["python3", "scripts/test_native_ots_upgrade_workflow_contract.py"],

        # Phase 7A prelaunch guardian application readiness
        ["python3", "scripts/test_phase7a_prelaunch_contracts.py"],

        # Phase 7A rate limit enforcement contract
        ["python3", "scripts/test_phase7a_rate_limit_contract.py"],

        # Mainnet prelaunch policy contract
        ["python3", "scripts/test_mainnet_prelaunch_policy_contract.py"],

        # Mandatory authorship key contract
        ["python3", "scripts/test_mandatory_authorship_key_contract.py"],

        # Gateway authorship proof contract
        ["python3", "scripts/test_gateway_authorship_proof_contract.py"],

        # M3 finalizer native compatibility contract
        ["python3", "scripts/test_m3_finalizer_native_compat_contract.py"],

        # Pre-scale record type/data architecture contracts
        ["python3", "scripts/test_record_type_separation_contract.py"],
        ["python3", "scripts/test_record_chain_data_arweave_archive_contract.py"],
        ["python3", "scripts/test_pre_scale_e2e_automation_contract.py"],
        ["python3", "scripts/test_live_test_phase_finalizer_contract.py"],
    ],
    "p0-main": [
        # p0-main is intentionally empty and deprecated.
        # Use p0-current instead.
    ],
    "guardian": [
        # Current Record-Chain Guardian lifecycle. The former issue/listing
        # automation tests were retired with gateway-v1 and must not make the
        # repository-integrity workflow fail before current tests can run.
        ["python3", "scripts/test_agent_e2e_journey_matrix.py"],
        ["python3", "scripts/test_mission_governance_contract.py"],
        ["python3", "scripts/test_guardian_activation_derivation_contract.py"],
        ["python3", "scripts/test_record_type_separation_contract.py"],
        ["python3", "scripts/test_gateway_authorship_proof_contract.py"],
        ["node", "downloads/test-record-chain-builder.mjs"],
        ["node", "scripts/test_builder_linked_guardian_disabled.mjs"],
        ["node", "scripts/test_legacy_guardian_retirement_tool_deprecated.mjs"],
        [
            "env", "PYTHONPATH=apps/record_chain_intake_gateway", "python3", "-m", "pytest",
            "apps/record_chain_intake_gateway/tests/test_guardian_identifier_validation.py",
            "apps/record_chain_intake_gateway/tests/test_guardian_retirement_target_binding.py",
            "apps/record_chain_intake_gateway/tests/test_linked_guardian_disabled.py",
            "apps/record_chain_intake_gateway/tests/test_optional_guardian_application_from_echo_verification.py",
            "apps/record_chain_intake_gateway/tests/test_write_mode_config_consistency.py",
            "tests/test_record_chain_guardian_retirement_flow.py",
            "tests/test_governance_entity_full_lifecycle.py",
            "-q",
        ],
    ],
    "chronicle": [
        ["python3", "scripts/generate_nft_chronicle_context.py"],
        ["git", "diff", "--exit-code", "--", "nft-text-descriptions/chronicle-full.md", "nft-text-descriptions/chronicle-abridged.md", "nft-text-descriptions/chronicle-ultra-brief.md", "nft-text-descriptions/chronicle-agent-context.md", "nft-text-descriptions/chronicle-index.json", "nft-text-descriptions/chronicle-summary.json", "api/agent-required-reading.json", "api/agent-task-router.v1.json", "api/context-load-map.json"],
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
        ["python3", "scripts/test_readback_hash_parity.py"],
        ["python3", "scripts/test_readback_hash_policy.py"],
        ["python3", "scripts/test_builder_oath_readback_canonical_output.py"],
    ],
    "agent-start-docs": [
        ["python3", "scripts/test_agent_start_docs.py"],
        ["python3", "scripts/test_agent_start_api.py"],
        ["node", "examples/github-app-backend/test-gateway-error-recovery-context.mjs"],
    ],
    "legacy-regressions": [
        ["python3", "scripts/check_consistency.py"],
    ],
    "fast-regression": [
        ["python3", "scripts/test_workflows_do_not_reference_missing_scripts.py"],
        ["python3", "scripts/test_workflow_permissions.py"],
        ["python3", "scripts/test_deep_integrity_group_nonempty.py"],
        ["python3", "scripts/check_public_core_consistency.py"],
        ["python3", "scripts/test_homepage_live_signals.py"],
        ["python3", "scripts/test_homepage_mobile_layout.py"],
        ["python3", "scripts/test_homepage_formation_window.py"],
        ["bash", "scripts/test-homepage-p0-agent-first.sh"],
    ],
    "live-site": [
        ["python3", "scripts/smoke_live_zero_clone_builder_bundles.py", "--site", "https://www.trinityaccord.org"],
        ["python3", "scripts/smoke_external_agent_entrypoint_journeys.py", "--site", "https://www.trinityaccord.org"],
        ["python3", "scripts/diagnose_live_propagation.py"],
    ],
    "live-site-swarm": [
        ["python3", "scripts/smoke_external_agent_concurrent_preflight_swarm.py", "--agents", "20", "--workers", "8", "--min-success-ratio", "0.9"],
    ],
    "live-site-gateway-core": [
        ["python3", "scripts/smoke_live_external_agent_three_core_preflight.py"],
        ["python3", "scripts/smoke_live_zero_clone_authorship_closure.py"],
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
