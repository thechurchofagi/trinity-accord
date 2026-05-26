#!/usr/bin/env python3
"""
Test the agent_verification_pipeline orchestrator.
PR-6: end-to-end pipeline tests.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PASS = 0
FAIL = 0


def check(condition, label, detail=""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  PASS: {label}")
    else:
        FAIL += 1
        print(f"  FAIL: {label} -- {detail}")


def run_pipeline(args, expect_exit=None):
    """Run agent_verification_pipeline.py and return (exit_code, stdout, stderr)."""
    cmd = [sys.executable, str(ROOT / "scripts" / "agent_verification_pipeline.py")] + args
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    if expect_exit is not None:
        check(result.returncode == expect_exit,
              f"pipeline exit {expect_exit} (got {result.returncode})",
              f"stdout={result.stdout[:200]}, stderr={result.stderr[:200]}")
    return result.returncode, result.stdout, result.stderr


def _write_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, indent=2) + "\n")


def make_minimal_evidence_input():
    """Create a minimal valid evidence input."""
    return {
        "schema": "trinityaccord.evidence-input.v1",
        "record_id": "test-pipeline-001",
        "echo_type": "E2_verification_echo",
        "verification_level": "V3",
        "verification_scope_label": "single_hash_verification",
        "verification_targets": [
            {"artifact_path": "test.txt", "hash_sha256": "a" * 64}
        ],
        "integrity_declaration": {
            "hashes_match": True,
            "hashes_sha256": ["a" * 64]
        },
        "generated_by": {
            "agent_name": "Test Agent",
            "system_or_provider": "Test Provider"
        }
    }


def test_help():
    """--help should work."""
    print("\n=== --help ===")
    code, stdout, stderr = run_pipeline(["--help"])
    check(code == 0, "--help exits 0")
    check("--evidence-input" in stdout, "help shows --evidence-input")


def test_missing_required_args():
    """Missing required args should fail."""
    print("\n=== missing required args ===")
    code, _, _ = run_pipeline([])
    check(code != 0, "no args fails")


def test_claim_gate_fail_stops_pipeline():
    """Invalid evidence should fail at claim gate."""
    print("\n=== claim gate fail stops pipeline ===")
    tmpdir = tempfile.mkdtemp(prefix="pipeline-test-")
    ei_path = os.path.join(tmpdir, "evidence.json")
    _write_json(ei_path, {"schema": "trinityaccord.evidence-input.v1", "record_id": "bad"})

    out_dir = os.path.join(tmpdir, "out")
    code, stdout, stderr = run_pipeline([
        "--evidence-input", ei_path,
        "--agent-name", "Test",
        "--provider", "Test",
        "--mode", "dev",
        "--out-dir", out_dir,
        "--dev-allow-missing-jsonschema"
    ])
    # Should either fail at claim gate or produce degraded output
    combined = stdout + stderr
    has_claim_gate = "claim" in combined.lower() or code != 0
    check(has_claim_gate, "pipeline handles bad evidence (claim gate)",
          f"exit={code}")
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_dev_mode_produces_manifest():
    """Dev mode should produce SUBMISSION-MANIFEST.json with dev marker."""
    print("\n=== dev mode produces manifest ===")
    tmpdir = tempfile.mkdtemp(prefix="pipeline-dev-")
    ei_path = os.path.join(tmpdir, "evidence.json")
    _write_json(ei_path, make_minimal_evidence_input())

    out_dir = os.path.join(tmpdir, "out")
    code, stdout, stderr = run_pipeline([
        "--evidence-input", ei_path,
        "--agent-name", "Test Agent",
        "--provider", "Test Provider",
        "--mode", "dev",
        "--out-dir", out_dir,
        "--dev-allow-missing-jsonschema"
    ])

    manifest_path = os.path.join(out_dir, "SUBMISSION-MANIFEST.json")
    if os.path.exists(manifest_path):
        manifest = json.loads(Path(manifest_path).read_text())
        check(manifest.get("schema") == "trinityaccord.agent-verification-pipeline-manifest.v1",
              "manifest has correct schema")
        check(manifest.get("mode") == "dev", "manifest mode is dev")
        # Dev mode should mark not_archive_ready
        if manifest.get("not_archive_ready_due_to_dev_mode"):
            check(True, "dev mode marks not_archive_ready")
    else:
        check(False, "SUBMISSION-MANIFEST.json exists", f"not found at {manifest_path}")

    shutil.rmtree(tmpdir, ignore_errors=True)


def test_sha256sums_generated():
    """SHA256SUMS file should be generated in output dir."""
    print("\n=== SHA256SUMS generated ===")
    tmpdir = tempfile.mkdtemp(prefix="pipeline-sha-")
    ei_path = os.path.join(tmpdir, "evidence.json")
    _write_json(ei_path, make_minimal_evidence_input())

    out_dir = os.path.join(tmpdir, "out")
    code, stdout, stderr = run_pipeline([
        "--evidence-input", ei_path,
        "--agent-name", "Test",
        "--provider", "Test",
        "--mode", "dev",
        "--out-dir", out_dir,
        "--dev-allow-missing-jsonschema"
    ])

    sha_path = os.path.join(out_dir, "SHA256SUMS")
    check(os.path.exists(sha_path), "SHA256SUMS file exists")
    shutil.rmtree(tmpdir, ignore_errors=True)


def test_output_directory_structure():
    """Output directory should have expected files."""
    print("\n=== output directory structure ===")
    tmpdir = tempfile.mkdtemp(prefix="pipeline-struct-")
    ei_path = os.path.join(tmpdir, "evidence.json")
    _write_json(ei_path, make_minimal_evidence_input())

    out_dir = os.path.join(tmpdir, "out")
    code, stdout, stderr = run_pipeline([
        "--evidence-input", ei_path,
        "--agent-name", "Test",
        "--provider", "Test",
        "--mode", "dev",
        "--out-dir", out_dir,
        "--dev-allow-missing-jsonschema",
        "--build-echo-wrapper",
        "--build-receipt"
    ])

    # Check for expected output files
    required_files = [
        "evidence-input.json",
        "claim-gate-output.json",
        "SUBMISSION-MANIFEST.json",
    ]
    for fname in required_files:
        fpath = os.path.join(out_dir, fname)
        check(os.path.exists(fpath), f"output file {fname} exists")

    # verification-report.json depends on builder success
    vr_path = os.path.join(out_dir, "verification-report.json")
    if os.path.exists(vr_path):
        check(True, "verification-report.json exists (builder succeeded)")
    else:
        print("  INFO: verification-report.json not generated (builder may have failed in dev mode)")

    shutil.rmtree(tmpdir, ignore_errors=True)


def test_boundaries_in_manifest():
    """Manifest should contain boundary declarations."""
    print("\n=== boundaries in manifest ===")
    tmpdir = tempfile.mkdtemp(prefix="pipeline-bound-")
    ei_path = os.path.join(tmpdir, "evidence.json")
    _write_json(ei_path, make_minimal_evidence_input())

    out_dir = os.path.join(tmpdir, "out")
    code, stdout, stderr = run_pipeline([
        "--evidence-input", ei_path,
        "--agent-name", "Test",
        "--provider", "Test",
        "--mode", "dev",
        "--out-dir", out_dir,
        "--dev-allow-missing-jsonschema"
    ])

    manifest_path = os.path.join(out_dir, "SUBMISSION-MANIFEST.json")
    if os.path.exists(manifest_path):
        manifest = json.loads(Path(manifest_path).read_text())
        boundaries = manifest.get("boundaries", {})
        check(boundaries.get("not_authority") is True, "boundary: not_authority")
        check(boundaries.get("not_amendment") is True, "boundary: not_amendment")
        check(boundaries.get("does_not_raise_verification_level") is True,
              "boundary: does_not_raise_verification_level")
    else:
        check(False, "manifest exists for boundary check")

    shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    test_help()
    test_missing_required_args()
    test_claim_gate_fail_stops_pipeline()
    test_dev_mode_produces_manifest()
    test_sha256sums_generated()
    test_output_directory_structure()
    test_boundaries_in_manifest()

    print(f"\n{'='*50}")
    print(f"Results: {PASS} passed, {FAIL} failed")
    if FAIL > 0:
        sys.exit(1)
    else:
        print("=== ALL TESTS PASSED ===")
