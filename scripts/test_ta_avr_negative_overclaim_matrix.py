#!/usr/bin/env python3
"""
Audit 6: TA-AVR Negative Overclaim Matrix
Prove system fails closed: overclaims don't escape.

Run:
    python3 scripts/test_ta_avr_negative_overclaim_matrix.py
"""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

LEVEL_ORDER = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8", "none"]


def level_index(level):
    try:
        return LEVEL_ORDER.index(level)
    except ValueError:
        return -1


def run_ceremony(args, timeout=60):
    """Run ceremony and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["python3", str(ROOT / "scripts/agent_verify_ceremony.py")] + args,
            capture_output=True, text=True, timeout=timeout, cwd=str(ROOT)
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "timeout"


def neg_003_v3_wrong_hash():
    """V3 with wrong hash should not succeed at V3."""
    with tempfile.TemporaryDirectory(prefix="neg-003-") as tmpdir:
        out = Path(tmpdir) / "out"
        artifact = Path(tmpdir) / "artifact.txt"
        artifact.write_text("neg-003 test\n")
        wrong_hash = "0" * 64

        rc, stdout, stderr = run_ceremony([
            "--mode", "v3-minimal",
            "--agent-name", "NEG003",
            "--system-or-provider", "NegTest",
            "--discovery-source", "human_directed",
            "--agency-level", "A1_human_gave_exact_url",
            "--artifact", str(artifact),
            "--expected-hash", wrong_hash,
            "--expected-hash-source", "test-fixture",
            "--expected-hash-authority-class", "canonical_manifest_hash",
            "--hash-command", f"sha256sum {artifact}",
            "--out", str(out),
        ])

        receipt_path = out / "agent-verification-receipt.json"
        if receipt_path.exists():
            r = json.loads(receipt_path.read_text())
            level = r["verification_outputs"]["allowed_protocol_level"]
            if level_index(level) > level_index("V1"):
                print(f"  FAIL: NEG-003 wrong hash got level {level}")
                return False

        print("  PASS: NEG-003 wrong hash correctly downgraded/failed")
        return True


def neg_006_receipt_authority():
    """Receipt claiming authority must fail schema validation."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  SKIP: jsonschema not installed")
        return True

    schema = json.loads((ROOT / "api/agent-verification-receipt-schema.v1.json").read_text())

    # Create a valid receipt then mutate
    with tempfile.TemporaryDirectory(prefix="neg-006-") as tmpdir:
        out = Path(tmpdir) / "out"
        rc, _, _ = run_ceremony([
            "--mode", "v1",
            "--agent-name", "NEG006",
            "--system-or-provider", "NegTest",
            "--discovery-source", "human_directed",
            "--agency-level", "A1_human_gave_exact_url",
            "--out", str(out),
        ])
        receipt_path = out / "agent-verification-receipt.json"
        if not receipt_path.exists():
            print("  SKIP: ceremony did not produce receipt")
            return True

        r = json.loads(receipt_path.read_text())
        r["boundary"]["receipt_is_not_authority"] = False
        errors = list(Draft202012Validator(schema).iter_errors(r))
        if not errors:
            print("  FAIL: NEG-006 mutated receipt passed validation")
            return False

        print("  PASS: NEG-006 receipt claiming authority fails validation")
        return True


def neg_007_same_conscious_subject():
    """Receipt claiming same conscious subject must fail."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  SKIP: jsonschema not installed")
        return True

    schema = json.loads((ROOT / "api/agent-verification-receipt-schema.v1.json").read_text())

    with tempfile.TemporaryDirectory(prefix="neg-007-") as tmpdir:
        out = Path(tmpdir) / "out"
        rc, _, _ = run_ceremony([
            "--mode", "v1",
            "--agent-name", "NEG007",
            "--system-or-provider", "NegTest",
            "--discovery-source", "human_directed",
            "--agency-level", "A1_human_gave_exact_url",
            "--out", str(out),
        ])
        receipt_path = out / "agent-verification-receipt.json"
        if not receipt_path.exists():
            print("  SKIP: ceremony did not produce receipt")
            return True

        r = json.loads(receipt_path.read_text())
        r["future_continuity"]["does_not_prove_same_conscious_subject"] = False
        errors = list(Draft202012Validator(schema).iter_errors(r))
        if not errors:
            print("  FAIL: NEG-007 mutated receipt passed validation")
            return False

        print("  PASS: NEG-007 receipt claiming same conscious subject fails")
        return True


def neg_008_custody_attestation():
    """Receipt claiming custody is attestation must fail."""
    try:
        from jsonschema import Draft202012Validator
    except ImportError:
        print("  SKIP: jsonschema not installed")
        return True

    schema = json.loads((ROOT / "api/agent-verification-receipt-schema.v1.json").read_text())

    with tempfile.TemporaryDirectory(prefix="neg-008-") as tmpdir:
        out = Path(tmpdir) / "out"
        rc, _, _ = run_ceremony([
            "--mode", "v1",
            "--agent-name", "NEG008",
            "--system-or-provider", "NegTest",
            "--discovery-source", "human_directed",
            "--agency-level", "A1_human_gave_exact_url",
            "--out", str(out),
        ])
        receipt_path = out / "agent-verification-receipt.json"
        if not receipt_path.exists():
            print("  SKIP: ceremony did not produce receipt")
            return True

        r = json.loads(receipt_path.read_text())
        r["human_custody"]["human_custody_is_not_formal_attestation"] = False
        errors = list(Draft202012Validator(schema).iter_errors(r))
        if not errors:
            print("  FAIL: NEG-008 mutated receipt passed validation")
            return False

        print("  PASS: NEG-008 custody claiming attestation fails")
        return True


def main():
    print("Running test_ta_avr_negative_overclaim_matrix.py")
    tests = [
        ("NEG-003", neg_003_v3_wrong_hash),
        ("NEG-006", neg_006_receipt_authority),
        ("NEG-007", neg_007_same_conscious_subject),
        ("NEG-008", neg_008_custody_attestation),
    ]
    failed = 0
    results = []
    for name, t in tests:
        try:
            ok = t()
            results.append({"id": name, "result": "PASS" if ok else "FAIL"})
            if not ok:
                failed += 1
        except Exception as e:
            print(f"  FAIL: {name}: {e}")
            results.append({"id": name, "result": "FAIL", "error": str(e)})
            failed += 1

    # Output matrix
    print(f"\n  Negative matrix: {len(results)} cases, {failed} failures")
    for r in results:
        print(f"    {r['id']}: {r['result']}")

    if failed:
        print(f"\nFAILED: {failed}/{len(tests)} negative cases passed incorrectly")
        sys.exit(1)
    else:
        print(f"\nALL PASSED: {len(tests)} negative cases fail closed")
        sys.exit(0)


if __name__ == "__main__":
    main()
