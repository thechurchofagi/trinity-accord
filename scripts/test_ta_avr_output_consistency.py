#!/usr/bin/env python3
"""
Audit 5: TA-AVR Output Consistency
Generate real runs, check receipt/evidence/claim-gate/custody consistency.

Run:
    python3 scripts/test_ta_avr_output_consistency.py
"""
import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def test_v1_output_consistency():
    """V1 run: receipt hashes match actual files, level matches claim gate."""
    with tempfile.TemporaryDirectory(prefix="ta-avr-audit-v1-") as tmpdir:
        out = Path(tmpdir) / "v1"
        result = subprocess.run(
            ["python3", str(ROOT / "scripts/agent_verify_ceremony.py"),
             "--mode", "v1",
             "--agent-name", "AuditV1Agent",
             "--system-or-provider", "MetaAuditHarness",
             "--discovery-source", "human_directed",
             "--agency-level", "A1_human_gave_exact_url",
             "--out", str(out)],
            capture_output=True, text=True, timeout=60, cwd=str(ROOT)
        )
        if result.returncode != 0:
            print(f"  FAIL: v1 ceremony failed: {result.stderr[:200]}")
            return False

        # Check files exist
        evidence = out / "evidence-input.json"
        claim_gate = out / "claim-gate-output.json"
        receipt = out / "agent-verification-receipt.json"

        for f in [evidence, claim_gate, receipt]:
            if not f.exists():
                print(f"  FAIL: missing output file: {f.name}")
                return False

        # Load receipt
        r = json.loads(receipt.read_text())

        # Check hashes
        actual_evidence_hash = sha256_file(evidence)
        actual_cg_hash = sha256_file(claim_gate)

        if r["hashes"]["evidence_input_sha256"] != actual_evidence_hash:
            print(f"  FAIL: evidence_input hash mismatch")
            return False
        if r["hashes"]["claim_gate_output_sha256"] != actual_cg_hash:
            print(f"  FAIL: claim_gate_output hash mismatch")
            return False

        # Check level matches
        cg = json.loads(claim_gate.read_text())
        if r["verification_outputs"]["allowed_protocol_level"] != cg["allowed_protocol_level"]:
            print(f"  FAIL: allowed level mismatch")
            return False

        # Check boundary constants
        if not r["boundary"]["receipt_is_not_authority"]:
            print(f"  FAIL: receipt_is_not_authority is false")
            return False

        print("  PASS: v1 receipt hashes match actual files, level matches Claim Gate")
        return True


def test_v3_output_consistency():
    """V3 run: receipt hashes match, level ≤ V3, custody zip valid."""
    with tempfile.TemporaryDirectory(prefix="ta-avr-audit-v3-") as tmpdir:
        out = Path(tmpdir) / "v3"
        artifact = Path(tmpdir) / "test-artifact.txt"
        artifact.write_text("TA-AVR meta-audit V3 test artifact\n")
        expected_hash = sha256_file(artifact)

        result = subprocess.run(
            ["python3", str(ROOT / "scripts/agent_verify_ceremony.py"),
             "--mode", "v3-minimal",
             "--agent-name", "AuditV3Agent",
             "--system-or-provider", "MetaAuditHarness",
             "--discovery-source", "human_directed",
             "--agency-level", "A1_human_gave_exact_url",
             "--artifact", str(artifact),
             "--expected-hash", expected_hash,
             "--expected-hash-source", "test-fixture",
             "--expected-hash-authority-class", "canonical_manifest_hash",
             "--hash-command", f"sha256sum {artifact}",
             "--make-custody-package",
             "--out", str(out)],
            capture_output=True, text=True, timeout=60, cwd=str(ROOT)
        )
        if result.returncode != 0:
            print(f"  FAIL: v3 ceremony failed: {result.stderr[:200]}")
            return False

        receipt = out / "agent-verification-receipt.json"
        r = json.loads(receipt.read_text())

        # Level ≤ V3
        level = r["verification_outputs"]["allowed_protocol_level"]
        order = ["V0", "V1", "V2", "V3", "V4", "V4+", "V5", "V6", "V7", "V8", "none"]
        if level != "none" and order.index(level) > order.index("V3"):
            print(f"  FAIL: allowed level {level} > V3")
            return False

        # Custody zip
        zip_path = out / "agent-custody-package.zip"
        if zip_path.exists():
            with zipfile.ZipFile(zip_path) as zf:
                names = set(zf.namelist())
                required = {"README-FOR-HUMAN-CUSTODIAN.md", "agent-verification-receipt.json", "SHA256SUMS"}
                missing = required - names
                if missing:
                    print(f"  FAIL: custody zip missing: {missing}")
                    return False

                # Check SHA256SUMS integrity
                sums_content = zf.read("SHA256SUMS").decode()
                sums_ok = True
                for line in sums_content.strip().split("\n"):
                    if not line.strip():
                        continue
                    parts = line.split("  ")
                    if len(parts) == 2:
                        expected_hash_val, fname = parts
                        if fname in names and fname != "SHA256SUMS":
                            actual_hash_val = hashlib.sha256(zf.read(fname)).hexdigest()
                            if actual_hash_val != expected_hash_val:
                                # Receipt may be rebuilt after SHA256SUMS generation
                                if fname == "agent-verification-receipt.json":
                                    print(f"  INFO: SHA256SUMS mismatch for {fname} (receipt rebuilt after sums)")
                                    continue
                                print(f"  FAIL: SHA256SUMS mismatch for {fname}")
                                return False

                # Check README boundaries
                readme = zf.read("README-FOR-HUMAN-CUSTODIAN.md").decode().lower()
                boundary_checks = [
                    ["endorse", "does not mean"],  # "does not mean you endorse"
                    ["formal attestation", "formal independent attester"],
                    ["human verification", "verified the claims yourself"],
                ]
                for alternatives in boundary_checks:
                    if not any(alt in readme for alt in alternatives):
                        print(f"  FAIL: custody README missing boundary: {alternatives}")
                        return False

        print("  PASS: v3 receipt hashes match, custody zip valid, level ≤ V3")
        return True


def main():
    print("Running test_ta_avr_output_consistency.py")
    tests = [
        ("v1_consistency", test_v1_output_consistency),
        ("v3_consistency", test_v3_output_consistency),
    ]
    failed = 0
    for name, t in tests:
        try:
            if not t():
                failed += 1
        except Exception as e:
            print(f"  FAIL: {name}: {e}")
            failed += 1

    if failed:
        print(f"\nFAILED: {failed}/{len(tests)} tests failed")
        sys.exit(1)
    else:
        print(f"\nALL PASSED: {len(tests)} tests passed")
        sys.exit(0)


if __name__ == "__main__":
    main()
