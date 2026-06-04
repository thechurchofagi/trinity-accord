#!/usr/bin/env python3
"""p0-current must include required record-chain-first mainline checks."""
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
p0 = groups.get("p0-current")
if not p0:
    print("FAIL: p0-current group missing")
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
    "python3 scripts/check_active_public_routes.py",
    "python3 scripts/test_p0_uses_public_core_consistency.py",

    # P0 group guards
    "python3 scripts/test_deep_integrity_includes_pages_build.py",
    "python3 scripts/test_public_core_consistency_required_links.py",
    "python3 scripts/test_sitemap_permalink_parser_uses_yaml.py",
    "python3 scripts/test_generate_sitemap_docstring_recursive_api.py",

    # Current route/taxonomy
    "python3 scripts/test_write_workflows_no_fail_open_rebase.py",
    "python3 scripts/test_workflow_warning_allowlist.py",
    "python3 scripts/test_agent_first_contact_echo_types_canonical.py",
    "python3 scripts/test_agent_facing_pure_echo_routes_canonical.py",
    "python3 scripts/test_links_expose_first_contact_entrypoints.py",
    "python3 scripts/test_first_contact_text_no_stale_route_guidance.py",
    "python3 scripts/test_agent_exit_readback_policy.py",
    "python3 scripts/test_v30_final_index_contract.py",
    "python3 scripts/test_v30_final_closure_report_contract.py",
    "python3 scripts/test_changelog_v30_5_contract.py",
    "python3 scripts/test_public_api_source_digest_if_present.py",

    # Discovery entrypoint contract
    "python3 scripts/test_well_known_exposes_agent_first_contact_contract.py",
    "python3 scripts/test_discovery_entrypoints_cover_full_agent_journey.py",

    # Pages deploy guards
    "python3 scripts/test_deploy_pages_workflow_contract.py",
    "python3 scripts/test_pages_build_contains_agent_discovery.py",
    "python3 scripts/test_pages_custom_domain_contract.py",
    "python3 scripts/test_deploy_pages_action_allowlist.py",
    "python3 scripts/test_deploy_pages_workflow_contract_is_static.py",

    # External agent journey smoke guards
    "python3 scripts/test_external_agent_journey_swarm_smoke_contract.py",
    "python3 scripts/test_external_agent_entrypoint_journey_smoke_contract.py",
    "python3 scripts/test_external_write_lifecycle_canary_contract.py",
    "python3 scripts/test_live_canary_policy_contract.py",
    "python3 scripts/test_external_agent_docs_zero_clone_alignment.py",
    "python3 scripts/test_external_agent_docs_core_routes_clarity.py",
    "python3 scripts/test_external_agent_examples_match_live_smokes.py",

    # before_leaving exit/readback contract
    "python3 scripts/test_agent_output_policy_before_leaving_exit_contract.py",

    # Generated drift
    "python3 scripts/generate_public_home_status.py --check",
    "python3 scripts/test_home_public_status_sync.py",

    # Zero-clone builder bundle guards (current)
    "python3 scripts/test_formal_builder_bundles_contract.py",
    "python3 scripts/test_external_agent_operation_examples_contract.py",
    "python3 scripts/test_export_formal_builder_bundles.py",
    "python3 scripts/test_download_helper_covers_all_routes.py",
    "python3 scripts/test_zero_clone_routes_in_first_contact.py",
    "python3 scripts/test_zero_clone_docs_cover_all_agent_types.py",
    "python3 scripts/test_formal_builder_bundle_api_matches_manifests.py",
    "python3 scripts/test_formal_builder_bundle_dependency_closure.py",
    "python3 scripts/test_formal_builder_bundles_are_executable.py",
    "python3 scripts/test_formal_builder_bundles_default_authorship_smoke.py",
    "python3 scripts/test_formal_builder_bundle_signature_contract.py",
    "python3 scripts/verify_formal_builder_bundle_signatures.py",

    # CI hardening
    "python3 scripts/test_run_ci_group_timeouts.py",

    # v30.3 authorship closure
    "python3 scripts/test_zero_clone_authorship_dependency_closure.py",
    "python3 scripts/test_authorship_helpers_are_cwd_independent.py",

    # Phase 6B security hotfix (current)
    "python3 scripts/test_no_secret_material_committed.py",
    "python3 scripts/test_no_private_key_material_committed.py",
    "python3 scripts/test_phase6b_hotfix.py",
    "python3 scripts/test_phase_6b_hotfix_contract.py",
    "python3 scripts/test_render_deploy_boundary_contract.py",
    "python3 scripts/test_legacy_isolation_contract.py",
    "python3 scripts/test_public_wording_phase6_contract.py",

    # Phase 6B test registry contract
    "python3 scripts/test_phase6b_test_registry_contract.py",
]

missing = [r for r in required if r not in cmds]
if missing:
    print("FAIL: p0-current missing required command(s):")
    for m in missing:
        print("  -", m)
    sys.exit(1)

print("PASS: p0-current includes required record-chain-first mainline checks")
