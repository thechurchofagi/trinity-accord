#!/usr/bin/env python3
"""p0-main must include required main-function drift and router checks."""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
path = ROOT / "scripts" / "run_ci_group.py"
tree = ast.parse(path.read_text(encoding="utf-8"))

groups_node = None
for node in tree.body:
    if isinstance(node, ast.Assign):
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == "GROUPS":
                groups_node = node.value

if groups_node is None:
    print("FAIL: GROUPS not found")
    sys.exit(1)

groups = ast.literal_eval(groups_node)
p0 = groups.get("p0-main")
if not p0:
    print("FAIL: p0-main group missing")
    sys.exit(1)

cmds = {" ".join(cmd) for cmd in p0}

required = [
    # Public surface
    "python3 scripts/test_sitemap_public_sources_exist.py",
    "python3 scripts/test_sitemap_includes_nested_api_json.py",
    "python3 scripts/test_sitemap_permalink_matches_source.py",
    "python3 scripts/test_public_referenced_paths_exist.py",
    "python3 scripts/test_public_referenced_paths_core_set.py",
    "python3 scripts/test_public_api_sitemap_coverage.py",
    "python3 scripts/test_public_api_metadata_general_not_pass.py",
    "python3 scripts/test_public_api_metadata_tier_b_schema_required.py",
    "python3 scripts/test_public_api_metadata_completeness.py",
    "python3 scripts/test_main_pages_have_machine_counterparts.py",

    # Context / agent routing
    "python3 scripts/test_context_load_map.py",
    "python3 scripts/test_context_pack_inventory_paths.py",
    "python3 scripts/test_agent_p0_router_contract.py",
    "python3 scripts/test_e2_verification_echo_not_pure_echo.py",

    # Consistency split guard
    "python3 scripts/check_public_core_consistency.py",
    "python3 scripts/test_p0_uses_public_core_consistency.py",

    # P0 group guards
    "python3 scripts/test_deep_integrity_includes_pages_build.py",
    "python3 scripts/test_gateway_online_smoke_workflow.py",
    "python3 scripts/test_public_core_consistency_required_links.py",
    "python3 scripts/test_gateway_endpoint_contracts.py",
    "python3 scripts/test_sitemap_permalink_parser_uses_yaml.py",
    "python3 scripts/test_generate_sitemap_docstring_recursive_api.py",

    # v8 source audit fixes
    "python3 scripts/test_agent_submit_gateway_echo_types_canonical.py",
    "python3 scripts/test_write_workflows_no_fail_open_rebase.py",
    "python3 scripts/test_workflow_warning_allowlist.py",
    "python3 scripts/test_echo_triage_rate_classifier_ambiguity_guards.py",

    # v9 first-contact echo taxonomy + links + prose + exit/readback
    "python3 scripts/test_agent_first_contact_echo_types_canonical.py",
    "python3 scripts/test_agent_facing_pure_echo_routes_canonical.py",
    "python3 scripts/test_links_expose_first_contact_entrypoints.py",
    "python3 scripts/test_first_contact_text_no_stale_route_guidance.py",
    "python3 scripts/test_agent_exit_readback_policy.py",

    # v10 workflow taxonomy
    "python3 scripts/test_gateway_workflows_echo_types_canonical.py",

    # source_digest broad sweep
    "python3 scripts/test_public_api_source_digest_if_present.py",

    # v10 workflow echo taxonomy + docs coverage
    "python3 scripts/test_gateway_workflows_echo_types_canonical.py",

    # v11 builder readback file alias / CLI contract / readback contract
    "python3 scripts/test_builder_readback_file_aliases.py",
    "python3 scripts/test_gateway_workflow_builder_cli_contract.py",
    "python3 scripts/test_gateway_workflows_readback_contract.py",
    "python3 scripts/test_gateway_workflow_human_cli_contract.py",
    "python3 scripts/test_gateway_workflows_correction_scope_wording.py",

    # v12 post-submit readback contract
    "python3 scripts/test_gateway_workflows_post_submit_readback_contract.py",
    "python3 scripts/test_submit_success_does_not_equal_archived_wording.py",
    "python3 scripts/test_agent_task_router_submit_echo_reads_workflow_manual.py",
    "python3 scripts/test_agent_first_contact_echo_reads_workflow_manual.py",

    # v13 guardian workflow & final checklist
    "python3 scripts/test_guardian_listing_stage2_workflow_cli_contract.py",
    "python3 scripts/test_guardian_signed_echo_workflow_wording.py",
    "python3 scripts/test_gateway_workflows_final_checklist_post_submit.py",
    "python3 scripts/test_gateway_workflow_tables_are_contiguous.py",

    # v14 non-echo route workflow contract
    "python3 scripts/test_guardian_stage1_workflow_cli_contract.py",
    "python3 scripts/test_gateway_workflows_stage1_inputs_contract.py",
    "python3 scripts/test_first_contact_guardian_reads_workflow_manual.py",
    "python3 scripts/test_first_contact_guardian_stage1_cli_contract.py",
    "python3 scripts/test_first_contact_guardian_stage2_uses_cli_flags.py",
    "python3 scripts/test_first_contact_verification_routes_read_workflow_manual.py",
    "python3 scripts/test_task_router_guardian_reads_workflow_manual.py",

    # v15 discovery entrypoint contract
    "python3 scripts/test_well_known_exposes_agent_first_contact_contract.py",
    "python3 scripts/test_links_expose_gateway_workflow_contract.py",
    "python3 scripts/test_discovery_entrypoints_cover_full_agent_journey.py",

    # v16 live discovery smoke guards
    "python3 scripts/test_site_live_discovery_smoke_workflow.py",
    "python3 scripts/test_gateway_online_smoke_scope_is_clear.py",
    # v17 pages deploy discovery guards
    "python3 scripts/test_deploy_pages_workflow_contract.py",
    "python3 scripts/test_pages_build_contains_agent_discovery.py",

    # v18 pages custom domain / live smoke guards
    "python3 scripts/test_pages_custom_domain_contract.py",

    # v19 pages live cache diagnostics & action allowlist
    "python3 scripts/test_live_discovery_smoke_cache_diagnostics.py",
    "python3 scripts/test_pages_diagnose_cache_busted.py",
    "python3 scripts/test_deploy_pages_action_allowlist.py",

    # v21 external agent journey swarm smoke guards
    "python3 scripts/test_external_agent_journey_swarm_smoke_contract.py",
    "python3 scripts/test_site_agent_journey_swarm_workflow.py",

    # v22 external heterogeneous entrypoint journey smoke guards
    "python3 scripts/test_external_agent_entrypoint_journey_smoke_contract.py",
    "python3 scripts/test_site_agent_entrypoint_journey_workflow.py",

    # v24 zero-manual external write lifecycle canary guards
    "python3 scripts/test_external_write_lifecycle_canary_contract.py",
    "python3 scripts/test_site_agent_write_lifecycle_canary_workflow.py",
    "python3 scripts/test_live_canary_policy_contract.py",
    "python3 scripts/test_gateway_discovery_for_canary.py",
    "python3 scripts/test_no_stale_gateway_submit_endpoint.py",
    "python3 scripts/test_external_agent_docs_zero_clone_alignment.py",

    # before_leaving exit/readback contract
    "python3 scripts/test_agent_output_policy_before_leaving_exit_contract.py",

    # Generated drift
    "python3 scripts/check_verification_index_urllib.py --repo thechurchofagi/trinity-accord",
    "python3 scripts/generate_public_home_status.py --check",
    "python3 scripts/test_home_public_status_sync.py",

    # v28 zero-clone builder bundle guards
    "python3 scripts/test_formal_builder_bundles_contract.py",
    "python3 scripts/test_external_agent_operation_examples_contract.py",
    "python3 scripts/test_export_formal_builder_bundles.py",
    "python3 scripts/test_download_helper_covers_all_routes.py",
    "python3 scripts/test_zero_clone_routes_in_first_contact.py",
    "python3 scripts/test_zero_clone_docs_cover_all_agent_types.py",
    "python3 scripts/test_gateway_workflows_zero_clone_examples.py",

    # v28.1 zero-clone hardening
    "python3 scripts/test_formal_builder_bundle_api_matches_manifests.py",

    # v28.2 zero-clone dependency closure
    "python3 scripts/test_formal_builder_bundle_dependency_closure.py",
    "python3 scripts/test_formal_builder_bundles_are_executable.py",
    "python3 scripts/test_formal_builder_bundles_default_authorship_smoke.py",

    # v28.3 CI hardening
    "python3 scripts/test_deploy_pages_workflow_contract_is_static.py",
    "python3 scripts/test_run_ci_group_timeouts.py",

    # v29 homepage zero-clone paths
    "python3 scripts/test_homepage_exposes_zero_clone_agent_paths.py",

    # v29 signed builder bundle manifests
    "python3 scripts/test_formal_builder_bundle_signature_contract.py",
    "python3 scripts/verify_formal_builder_bundle_signatures.py",

    # v29 before_leaving schema
    "python3 scripts/test_agent_before_leaving_report_schema.py",

    # v29 concurrent preflight swarm contract
    "python3 scripts/test_concurrent_preflight_swarm_contract.py",

    # v29 agent live-health
    "python3 scripts/test_agent_live_health_contract.py",
]

missing = [r for r in required if r not in cmds]
if missing:
    print("FAIL: p0-main missing required command(s):")
    for m in missing:
        print("  -", m)
    sys.exit(1)

print("PASS: p0-main includes required main-function checks")
