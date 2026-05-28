#!/usr/bin/env python3
"""Test that the zero-clone authorship proof dependency closure is complete.

This test verifies that all files required for authorship proof generation
and attachment are present in the repository when referenced by
formal-builder-bundles.v1.json's shared_dependency_sets.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_authorship_proof_closure_files_exist():
    """All files listed in shared_dependency_sets.authorship_proof_closure must exist."""
    bundles_path = ROOT / "api" / "formal-builder-bundles.v1.json"
    assert bundles_path.exists(), f"Bundle manifest not found: {bundles_path}"

    bundles = json.loads(bundles_path.read_text(encoding="utf-8"))
    dep_sets = bundles.get("shared_dependency_sets", {})

    assert "authorship_proof_closure" in dep_sets, (
        "shared_dependency_sets.authorship_proof_closure missing from formal-builder-bundles.v1.json"
    )

    closure_files = dep_sets["authorship_proof_closure"]
    assert len(closure_files) >= 4, (
        f"authorship_proof_closure should have at least 4 files, got {len(closure_files)}"
    )

    missing = []
    for rel_path in closure_files:
        full_path = ROOT / rel_path
        if not full_path.exists():
            missing.append(rel_path)

    assert not missing, (
        f"Authorship proof dependency closure incomplete. Missing: {', '.join(missing)}"
    )


def test_closure_matches_gateway_payload_authorship_check():
    """The closure in the bundle manifest must reference the same file set as gateway_payload_authorship.py."""
    bundles_path = ROOT / "api" / "formal-builder-bundles.v1.json"
    bundles = json.loads(bundles_path.read_text(encoding="utf-8"))
    bundle_closure = set(bundles["shared_dependency_sets"]["authorship_proof_closure"])

    authorship_path = ROOT / "scripts" / "gateway_payload_authorship.py"
    authorship_src = authorship_path.read_text(encoding="utf-8")

    # Verify the Python source defines AUTHORSHIP_CLOSURE_FILES with the same 4 files
    expected_files = {
        "scripts/gateway_payload_authorship.py",
        "scripts/generate_agent_authorship_keypair.mjs",
        "scripts/attach_agent_authorship_proof.mjs",
        "scripts/build_agent_authorship_message.py",
        "scripts/agent_authorship_common.py",
    }

    # The Python AUTHORSHIP_CLOSURE_FILES lists the *dependency* files (not itself)
    # The JSON lists all 5 including gateway_payload_authorship.py
    # Both sets must match
    assert bundle_closure == expected_files, (
        f"Closure mismatch.\nBundle manifest: {sorted(bundle_closure)}\nExpected: {sorted(expected_files)}"
    )

    # Verify the Python source contains all the dependency paths
    for dep_file in [
        "generate_agent_authorship_keypair.mjs",
        "attach_agent_authorship_proof.mjs",
        "build_agent_authorship_message.py",
        "agent_authorship_common.py",
    ]:
        assert dep_file in authorship_src, (
            f"{dep_file} not referenced in gateway_payload_authorship.py AUTHORSHIP_CLOSURE_FILES"
        )


def test_bundles_using_closure_specify_dependency_sets():
    """Bundles that use authorship_proof_closure must declare dependency_sets."""
    bundles_path = ROOT / "api" / "formal-builder-bundles.v1.json"
    bundles = json.loads(bundles_path.read_text(encoding="utf-8"))

    expected_bundles = [
        "pure_echo",
        "v0_v5_agent_declared_archive",
        "guardian_application_stage_1",
        "guardian_signed_echo",
    ]

    for bundle_name in expected_bundles:
        assert bundle_name in bundles["bundles"], f"Bundle {bundle_name} not found"
        bundle = bundles["bundles"][bundle_name]
        assert "dependency_sets" in bundle, (
            f"Bundle {bundle_name} missing dependency_sets"
        )
        assert "authorship_proof_closure" in bundle["dependency_sets"], (
            f"Bundle {bundle_name} dependency_sets does not include authorship_proof_closure"
        )


def test_assert_authorship_closure_present_exists():
    """gateway_payload_authorship.py must define assert_authorship_closure_present()."""
    authorship_path = ROOT / "scripts" / "gateway_payload_authorship.py"
    src = authorship_path.read_text(encoding="utf-8")
    assert "def assert_authorship_closure_present():" in src, (
        "assert_authorship_closure_present() not found in gateway_payload_authorship.py"
    )
    assert "assert_authorship_closure_present()" in src, (
        "assert_authorship_closure_present() is defined but never called"
    )


if __name__ == "__main__":
    tests = [
        test_authorship_proof_closure_files_exist,
        test_closure_matches_gateway_payload_authorship_check,
        test_bundles_using_closure_specify_dependency_sets,
        test_assert_authorship_closure_present_exists,
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
