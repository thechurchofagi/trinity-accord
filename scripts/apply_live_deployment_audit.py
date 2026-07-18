#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one target, found {count}")
    return text.replace(old, new, 1)


workflow_path = ROOT / ".github/workflows/deploy-pages.yml"
workflow = workflow_path.read_text(encoding="utf-8")
workflow = replace_once(
    workflow,
    '      - "scripts/check_homepage_live_freshness.py"\n',
    '      - "scripts/check_homepage_live_freshness.py"\n'
    '      - "scripts/public_machine_deployment_contract.py"\n'
    '      - "scripts/smoke_live_discovery_contract.py"\n'
    '      - "scripts/smoke_live_discovery_contract_v2.py"\n'
    '      - "scripts/check_deployment_freshness_v2.py"\n',
    "deploy path filters",
)
workflow = workflow.replace(
    "python3 scripts/check_deployment_freshness.py --site-dir _site",
    "python3 scripts/check_deployment_freshness_v2.py --site-dir _site",
)
workflow = workflow.replace(
    "python3 scripts/check_deployment_freshness.py --site \"https://www.trinityaccord.org\"",
    "python3 scripts/check_deployment_freshness_v2.py --site \"https://www.trinityaccord.org\"",
)
workflow = workflow.replace(
    "python3 scripts/smoke_live_discovery_contract.py",
    "python3 scripts/smoke_live_discovery_contract_v2.py",
)
workflow = replace_once(
    workflow,
    "for i in 1 2 3 4 5 6; do",
    "for i in $(seq 1 12); do",
    "live smoke retry range",
)
workflow = workflow.replace("Live discovery smoke attempt ${i}/6...", "Live discovery smoke attempt ${i}/12...")
for required in (
    "scripts/smoke_live_discovery_contract_v2.py",
    "scripts/check_deployment_freshness_v2.py",
    "scripts/public_machine_deployment_contract.py",
):
    if required not in workflow:
        raise RuntimeError(f"workflow missing current checker {required}")
workflow_path.write_text(workflow, encoding="utf-8")

# Preserve the old command path as a compatibility wrapper while eliminating
# its stale hard-coded route taxonomy.
old_smoke = ROOT / "scripts/smoke_live_discovery_contract.py"
old_smoke.write_text(
    '''#!/usr/bin/env python3
"""Compatibility entrypoint for the current live discovery smoke."""
from smoke_live_discovery_contract_v2 import main


if __name__ == "__main__":
    raise SystemExit(main())
''',
    encoding="utf-8",
)

# Keep the old freshness module's marker/helper definitions for v2 imports,
# but route direct command execution to the complete current check.
old_freshness = ROOT / "scripts/check_deployment_freshness.py"
freshness = old_freshness.read_text(encoding="utf-8")
freshness = replace_once(
    freshness,
    '''if __name__ == "__main__":
    sys.exit(main())
''',
    '''if __name__ == "__main__":
    from check_deployment_freshness_v2 import main as current_main

    sys.exit(current_main())
''',
    "freshness compatibility main",
)
old_freshness.write_text(freshness, encoding="utf-8")

print("LIVE_DEPLOYMENT_AUDIT_PATCH_APPLIED")
