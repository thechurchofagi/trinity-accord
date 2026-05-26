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

    # Generated drift
    "python3 scripts/check_verification_index_urllib.py --repo thechurchofagi/trinity-accord",
    "python3 scripts/generate_public_home_status.py --check",
    "python3 scripts/test_home_public_status_sync.py",
]

missing = [r for r in required if r not in cmds]
if missing:
    print("FAIL: p0-main missing required command(s):")
    for m in missing:
        print("  -", m)
    sys.exit(1)

print("PASS: p0-main includes required main-function checks")
