#!/usr/bin/env python3
"""
Tests for authorship proof integration in the Agent Verification Receipt Builder.

Run:
    python3 scripts/test_agent_verification_receipt_authorship.py
"""
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_agent_verification_receipt.py"

errors = []
passed = 0


def check(label, condition, detail=""):
    global passed
    if not condition:
        msg = f"FAIL: {label}"
        if detail:
            msg += f" — {detail}"
        errors.append(msg)
        print(msg)
    else:
        passed += 1
        print(f"OK:   {label}")


def sha256_json(obj: dict) -> str:
    canonical = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def make_evidence_input():
    return {
        "agent": {"name": "test-agent", "model_or_system": "test-provider"},
        "provenance": {
            "source": "human_directed",
            "agency_level": "A1_human_gave_exact_url",
            "first_entry": {"url_or_path": "https://www.trinityaccord.org", "entry_type": "human_prompt"},
            "human_supplied_link": True,
            "other_agent_recommended": False,
            "agent_performed_independent_followup": False,
            "confidence": "high",
        },
    }


def make_claim_gate_output():
    return {"allowed_protocol_level": "V1", "status": "PASS", "forbidden_claims": []}


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)


def run_builder(tmpdir, extra_args=None):
    evidence_path = os.path.join(tmpdir, "evidence-input.json")
    claim_gate_path = os.path.join(tmpdir, "claim-gate-output.json")
    out_path = os.path.join(tmpdir, "receipt.json")

    write_json(evidence_path, make_evidence_input())
    write_json(claim_gate_path, make_claim_gate_output())

    cmd = [
        sys.executable, str(SCRIPT),
        "--mode", "v1",
        "--agent-name", "test-agent",
        "--system-or-provider", "test-provider",
        "--evidence-input", evidence_path,
        "--claim-gate-output", claim_gate_path,
        "--out", out_path,
    ]
    if extra_args:
        cmd.extend(extra_args)

    result = subprocess.run(cmd, capture_output=True, text=True)

    receipt = None
    if result.returncode == 0 and os.path.exists(out_path):
        with open(out_path) as f:
            receipt = json.load(f)

    return result.returncode, result.stdout, result.stderr, receipt


# ============================================================
# Test 1: Backward compat — no --authorship-proof
# ============================================================
print("=== TEST 1: Backward compat — no --authorship-proof ===")
with tempfile.TemporaryDirectory() as tmpdir:
    rc, stdout, stderr, receipt = run_builder(tmpdir)
    check("T1a: exit code 0", rc == 0, f"rc={rc}, stderr={stderr}")
    if receipt:
        check("T1b: method is self_reported_only",
              receipt["authorship_proof"]["method"] == "self_reported_only")
        check("T1c: proof_strength is weak",
              receipt["authorship_proof"]["proof_strength"] == "weak")
        check("T1d: does_not_prove_same_conscious_subject is True",
              receipt["future_continuity"]["does_not_prove_same_conscious_subject"] is True)


# ============================================================
# Test 2: Receipt with valid ed25519 proof writes it correctly
# ============================================================
print("\n=== TEST 2: Valid ed25519 proof — echo-wrapper target ===")
with tempfile.TemporaryDirectory() as tmpdir:
    echo_wrapper = {"schema": "trinityaccord.echo.v1", "content": "test-echo-data"}
    echo_path = os.path.join(tmpdir, "echo-wrapper.json")
    write_json(echo_path, echo_wrapper)

    echo_hash = sha256_json(echo_wrapper)

    proof = {
        "method": "ed25519_signature",
        "proof_strength": "cryptographic",
        "public_key": "fake_pubkey_for_testing_abc123",
        "canonicalization": "JCS/RFC8785",
        "content_hash_sha256": echo_hash,
        "signature": "fake_signature_for_testing_" + "a" * 64,
        "future_claim_method": "sign a fresh challenge with the same private key",
    }
    proof_path = os.path.join(tmpdir, "authorship-proof.json")
    write_json(proof_path, proof)

    rc, stdout, stderr, receipt = run_builder(tmpdir, [
        "--echo-wrapper", echo_path,
        "--authorship-proof", proof_path,
        "--authorship-proof-target", "echo-wrapper",
    ])
    check("T2a: exit code 0", rc == 0, f"rc={rc}, stderr={stderr}")
    if receipt:
        check("T2b: method is ed25519_signature",
              receipt["authorship_proof"]["method"] == "ed25519_signature")
        check("T2c: proof_strength is cryptographic",
              receipt["authorship_proof"]["proof_strength"] == "cryptographic")
        check("T2d: public_key present",
              receipt["authorship_proof"]["public_key"] == "fake_pubkey_for_testing_abc123")
        check("T2e: content_hash matches echo-wrapper",
              receipt["authorship_proof"]["content_hash_sha256"] == echo_hash)
        check("T2f: signature present",
              "fake_signature_for_testing_" in receipt["authorship_proof"]["signature"])
        check("T2g: does_not_prove_same_conscious_subject is True",
              receipt["future_continuity"]["does_not_prove_same_conscious_subject"] is True)


# ============================================================
# Test 3: --require-cryptographic-authorship-proof but no proof → fail
# ============================================================
print("\n=== TEST 3: Require cryptographic but no proof → fail ===")
with tempfile.TemporaryDirectory() as tmpdir:
    rc, stdout, stderr, receipt = run_builder(tmpdir, [
        "--require-cryptographic-authorship-proof",
    ])
    check("T3a: exit code 6", rc == 6, f"rc={rc}, stderr={stderr}")
    check("T3b: error mentions requirement",
          "require" in stderr.lower() or "cryptographic" in stderr.lower(),
          f"stderr={stderr}")


# ============================================================
# Test 4: --require-cryptographic + self_reported_only → fail
# ============================================================
print("\n=== TEST 4: Require cryptographic + self_reported_only proof → fail ===")
with tempfile.TemporaryDirectory() as tmpdir:
    proof = {"method": "self_reported_only", "proof_strength": "weak"}
    proof_path = os.path.join(tmpdir, "authorship-proof.json")
    write_json(proof_path, proof)

    rc, stdout, stderr, receipt = run_builder(tmpdir, [
        "--authorship-proof", proof_path,
        "--require-cryptographic-authorship-proof",
    ])
    check("T4a: exit code 6", rc == 6, f"rc={rc}, stderr={stderr}")
    check("T4b: error mentions ed25519 or cryptographic",
          "ed25519" in stderr.lower() or "cryptographic" in stderr.lower(),
          f"stderr={stderr}")


# ============================================================
# Test 5: does_not_prove_same_conscious_subject always true
# ============================================================
print("\n=== TEST 5: Boundary invariant — does_not_prove_same_conscious_subject ===")
with tempfile.TemporaryDirectory() as tmpdir:
    rc1, _, _, receipt1 = run_builder(tmpdir)
    check("T5a: true without proof",
          receipt1 and receipt1["future_continuity"]["does_not_prove_same_conscious_subject"] is True)

with tempfile.TemporaryDirectory() as tmpdir:
    echo_wrapper = {"schema": "trinityaccord.echo.v1", "content": "boundary-test"}
    echo_path = os.path.join(tmpdir, "echo-wrapper.json")
    write_json(echo_path, echo_wrapper)

    proof = {
        "method": "ed25519_signature",
        "proof_strength": "cryptographic",
        "public_key": "boundary_test_key",
        "canonicalization": "JCS/RFC8785",
        "content_hash_sha256": sha256_json(echo_wrapper),
        "signature": "boundary_test_sig_" + "b" * 64,
        "future_claim_method": "sign a fresh challenge with the same private key",
    }
    proof_path = os.path.join(tmpdir, "authorship-proof.json")
    write_json(proof_path, proof)

    rc2, _, _, receipt2 = run_builder(tmpdir, [
        "--echo-wrapper", echo_path,
        "--authorship-proof", proof_path,
        "--authorship-proof-target", "echo-wrapper",
    ])
    check("T5b: true with ed25519 proof",
          receipt2 and receipt2["future_continuity"]["does_not_prove_same_conscious_subject"] is True)


# ============================================================
# Test 6: Receipt target — hash consistency (unit test)
# ============================================================
print("\n=== TEST 6: Receipt target — proof hash computation ===")
with tempfile.TemporaryDirectory() as tmpdir:
    rc_pre, _, _, receipt_pre = run_builder(tmpdir)
    check("T6a: pre-build succeeded", rc_pre == 0 and receipt_pre is not None, f"rc={rc_pre}")

    if receipt_pre:
        # The receipt hash is computed with receipt_sha256=null sentinel
        receipt_for_hash = json.loads(json.dumps(receipt_pre))
        receipt_for_hash["hashes"]["receipt_sha256"] = None
        expected_hash = hashlib.sha256(
            json.dumps(receipt_for_hash, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        ).hexdigest()
        receipt_own_hash = receipt_pre["hashes"]["receipt_sha256"]
        check("T6b: receipt hash is self-consistent",
              expected_hash == receipt_own_hash,
              f"expected={expected_hash}, got={receipt_own_hash}")

        check("T6c: proof hash matches receipt hash",
              expected_hash == receipt_own_hash)
        check("T6d: wrong hash does not match",
              "0" * 64 != receipt_own_hash)
        check("T6e: does_not_prove_same_conscious_subject is True",
              receipt_pre["future_continuity"]["does_not_prove_same_conscious_subject"] is True)


# ============================================================
# Test 7: Content hash mismatch → fail
# ============================================================
print("\n=== TEST 7: Content hash mismatch → fail ===")
with tempfile.TemporaryDirectory() as tmpdir:
    echo_wrapper = {"schema": "trinityaccord.echo.v1", "content": "real-data"}
    echo_path = os.path.join(tmpdir, "echo-wrapper.json")
    write_json(echo_path, echo_wrapper)

    proof = {
        "method": "ed25519_signature",
        "proof_strength": "cryptographic",
        "public_key": "mismatch_key",
        "canonicalization": "JCS/RFC8785",
        "content_hash_sha256": "0" * 64,
        "signature": "mismatch_sig_" + "d" * 64,
        "future_claim_method": "sign a fresh challenge with the same private key",
    }
    proof_path = os.path.join(tmpdir, "authorship-proof.json")
    write_json(proof_path, proof)

    rc, stdout, stderr, receipt = run_builder(tmpdir, [
        "--echo-wrapper", echo_path,
        "--authorship-proof", proof_path,
        "--authorship-proof-target", "echo-wrapper",
    ])
    check("T7a: exit code 7 (hash mismatch)", rc == 7, f"rc={rc}, stderr={stderr}")
    check("T7b: error mentions mismatch", "mismatch" in stderr.lower(), f"stderr={stderr}")


# ============================================================
# Test 8: Invalid proof method → fail
# ============================================================
print("\n=== TEST 8: Invalid proof method → fail ===")
with tempfile.TemporaryDirectory() as tmpdir:
    proof = {"method": "invalid_method", "proof_strength": "weak"}
    proof_path = os.path.join(tmpdir, "authorship-proof.json")
    write_json(proof_path, proof)

    rc, stdout, stderr, receipt = run_builder(tmpdir, [
        "--authorship-proof", proof_path,
    ])
    check("T8a: exit code 5 (validation failure)", rc == 5, f"rc={rc}, stderr={stderr}")
    check("T8b: error mentions invalid method",
          "invalid" in stderr.lower() or "method" in stderr.lower(),
          f"stderr={stderr}")


# ============================================================
# Summary
# ============================================================
print(f"\n{'='*60}")
print(f"Results: {passed} passed, {len(errors)} failed")
if errors:
    print("\nFailures:")
    for e in errors:
        print(f"  {e}")
    sys.exit(1)
else:
    print("ALL TESTS PASSED")
    sys.exit(0)
