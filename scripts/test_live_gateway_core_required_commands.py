#!/usr/bin/env python3
"""Test that live-site-gateway-core CI group includes required smoke tests.

This test ensures the CI pipeline for live Gateway testing includes both:
1. smoke_live_external_agent_three_core_preflight.py (three core routes)
2. smoke_live_zero_clone_authorship_closure.py (authorship closure)
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_LIVE_GATEWAY_TESTS = [
    "scripts/smoke_live_external_agent_three_core_preflight.py",
    "scripts/smoke_live_zero_clone_authorship_closure.py",
]

REQUIRED_CI_GROUP = "live-site-gateway-core"


def find_ci_group_definition():
    """Find the file that defines CI groups and extract live-site-gateway-core."""
    # Check run_ci_group.py
    candidates = [
        ROOT / "scripts" / "run_ci_group.py",
        ROOT / "scripts" / "test_p0_main_required_commands.py",
        ROOT / ".github" / "workflows",
    ]

    # Search for CI group definitions in Python files
    for py_file in ROOT.rglob("*.py"):
        try:
            src = py_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if REQUIRED_CI_GROUP in src:
            return py_file, src

    # Search in YAML/YML files
    for yml_file in ROOT.rglob("*.yml"):
        try:
            src = yml_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if REQUIRED_CI_GROUP in src:
            return yml_file, src

    for yml_file in ROOT.rglob("*.yaml"):
        try:
            src = yml_file.read_text(encoding="utf-8")
        except Exception:
            continue
        if REQUIRED_CI_GROUP in src:
            return yml_file, src

    return None, None


def test_ci_group_file_exists():
    """There must be a file defining the live-site-gateway-core CI group."""
    path, src = find_ci_group_definition()
    assert path is not None, (
        f"No file found that defines CI group '{REQUIRED_CI_GROUP}'. "
        "Add it to scripts/run_ci_group.py or a CI workflow."
    )
    print(f"  Found in: {path.relative_to(ROOT)}")


def test_ci_group_includes_required_tests():
    """The live-site-gateway-core group must include both required smoke tests."""
    path, src = find_ci_group_definition()
    assert path is not None, "CI group definition file not found"

    for test_name in REQUIRED_LIVE_GATEWAY_TESTS:
        # Check for the script name (with or without scripts/ prefix)
        basename = Path(test_name).name
        assert basename in src or test_name in src, (
            f"'{test_name}' not found in CI group '{REQUIRED_CI_GROUP}' "
            f"(checked {path.relative_to(ROOT)}). "
            f"Add '{basename}' to the {REQUIRED_CI_GROUP} group."
        )


def test_required_test_files_exist():
    """The required smoke test scripts must exist in the repository."""
    for test_name in REQUIRED_LIVE_GATEWAY_TESTS:
        test_path = ROOT / test_name
        assert test_path.exists(), (
            f"Required test script not found: {test_name}"
        )


if __name__ == "__main__":
    tests = [
        test_ci_group_file_exists,
        test_ci_group_includes_required_tests,
        test_required_test_files_exist,
    ]
    failed = []
    for test in tests:
        try:
            test()
            print(f"  PASS: {test.__name__}")
        except Exception as e:
            print(f"  FAIL: {test.__name__}: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\nFAILED: {len(failed)} test(s): {', '.join(failed)}")
        sys.exit(1)
    else:
        print(f"\nALL {len(tests)} TESTS PASSED")
        sys.exit(0)
