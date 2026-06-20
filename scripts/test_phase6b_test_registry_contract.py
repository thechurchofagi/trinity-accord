#!/usr/bin/env python3
"""Phase 6B/6C test registry contract: verify critical test files exist and are wired into CI.

Checks that key test scripts are present and registered in:
  - run_current_system_tests.py (direct)
  - repository-integrity.yml (direct or indirect via run_current_system_tests.py)
  - deploy-pages.yml (direct or indirect via run_current_system_tests.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Critical test files that must exist and be wired into CI
REQUIRED_TESTS = [
    # Phase 6B
    "scripts/test_phase6b_hotfix.py",
    "scripts/test_phase_6b_hotfix_contract.py",
    "scripts/test_render_deploy_boundary_contract.py",
    "scripts/test_legacy_isolation_contract.py",
    "scripts/test_public_wording_phase6_contract.py",
    "scripts/test_no_secret_material_committed.py",
    "downloads/test-record-chain-builder.mjs",
    # Phase 6C
    "scripts/test_operator_secret_names_contract.py",
    "scripts/test_arweave_live_readiness_contract.py",
    "scripts/test_render_manual_deploy_contract.py",
    # Guardian activation
    "scripts/test_guardian_activation_derivation_contract.py",
]

# CI wiring targets
CI_WIRING = {
    "run_current_system_tests.py": ROOT / "scripts" / "run_current_system_tests.py",
    "repository-integrity.yml": ROOT / ".github" / "workflows" / "repository-integrity.yml",
    "deploy-pages.yml": ROOT / ".github" / "workflows" / "deploy-pages.yml",
}


def _test_is_in_ci(test_file: str, ci_text: str) -> bool:
    """Check if a test file is referenced in CI text (directly or by script name)."""
    basename = Path(test_file).name
    stem = Path(test_file).stem
    return basename in ci_text or stem in ci_text


def main() -> int:
    ok = True

    # 1. Check all required test files exist
    for test_file in REQUIRED_TESTS:
        p = ROOT / test_file
        if not p.exists():
            print(f"FAIL: missing required Phase 6B test file: {test_file}")
            ok = False
        else:
            print(f"PASS: {test_file} exists")

    # 2. Check direct wiring in run_current_system_tests.py
    runner_path = CI_WIRING["run_current_system_tests.py"]
    runner_text = runner_path.read_text(encoding="utf-8") if runner_path.exists() else ""

    for test_file in REQUIRED_TESTS:
        if _test_is_in_ci(test_file, runner_text):
            print(f"PASS: {test_file} wired into run_current_system_tests.py")
        else:
            print(f"FAIL: {test_file} NOT wired into run_current_system_tests.py")
            ok = False

    # 3. Check workflow files — either direct reference OR indirect via run_current_system_tests.py
    for wf_name in ["repository-integrity.yml", "deploy-pages.yml"]:
        wf_path = CI_WIRING[wf_name]
        if not wf_path.exists():
            print(f"FAIL: workflow missing: {wf_name}")
            ok = False
            continue

        wf_text = wf_path.read_text(encoding="utf-8")
        has_runner = "run_current_system_tests.py" in wf_text

        for test_file in REQUIRED_TESTS:
            directly = _test_is_in_ci(test_file, wf_text)
            indirectly = has_runner  # runner includes all its tests

            if directly:
                print(f"PASS: {test_file} directly wired into {wf_name}")
            elif indirectly:
                print(f"PASS: {test_file} indirectly wired into {wf_name} (via run_current_system_tests.py)")
            else:
                print(f"FAIL: {test_file} NOT wired into {wf_name}")
                ok = False

    if not ok:
        sys.exit(1)

    print("\nPASS: Phase 6B test registry contract verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
