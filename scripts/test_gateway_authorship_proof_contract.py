#!/usr/bin/env python3
"""test_gateway_authorship_proof_contract.py

Tests that the gateway correctly verifies Ed25519 authorship proofs.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"

sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))
from gateway.validation import validate_submission
from gateway.authorship import verify_authorship_proof

PASS = 0
FAIL = 0

def ok(msg):
    global PASS
    PASS += 1
    print(f"  PASS: {msg}")

def fail(msg, detail=""):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {msg}")
    if detail:
        print(f"        {detail}")

def build_echo_submission(key_dir):
    """Build a valid echo submission using the builder."""
    with tempfile.TemporaryDirectory() as td:
        body = Path(td) / "echo.md"
        body.write_text("Test echo for gateway verification.")
        out = Path(td) / "out.json"
        r = subprocess.run(
            ["node", str(BUILDER), "echo",
             "--actor-label", "Test Agent",
             "--provider", "Test Runtime",
             "--body-file", str(body),
             "--context-level", "CC-3",
             "--readback", "dummy",
             "--key-dir", str(key_dir),
             "--out", str(out)],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if out.exists():
            return json.loads(out.read_text())
    return None

def build_context_insufficient_submission(key_dir):
    """Build a context-insufficient submission."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        r = subprocess.run(
            ["node", str(BUILDER), "context-insufficient",
             "--actor-label", "Test Agent",
             "--provider", "Test Runtime",
             "--key-dir", str(key_dir),
             "--out", str(out)],
            capture_output=True, text=True, cwd=str(ROOT)
        )
        if out.exists():
            return json.loads(out.read_text())
    return None

def test_valid_echo_no_authorship_diagnostics():
    """Valid builder echo should have no authorship diagnostics."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission")
            return
        diags = validate_submission(sub)
        authorship_diags = [d for d in diags if "AUTHORSHIP" in (d.get("code") or "")]
        if not authorship_diags:
            ok("valid echo has no authorship diagnostics")
        else:
            fail("valid echo has authorship diagnostics", str(authorship_diags))

def test_valid_context_insufficient_no_authorship_diagnostics():
    """Valid context-insufficient should have no authorship diagnostics."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_context_insufficient_submission(key_dir)
        if not sub:
            fail("could not build context-insufficient submission")
            return
        diags = validate_submission(sub)
        authorship_diags = [d for d in diags if "AUTHORSHIP" in (d.get("code") or "")]
        if not authorship_diags:
            ok("valid context-insufficient has no authorship diagnostics")
        else:
            fail("valid context-insufficient has authorship diagnostics", str(authorship_diags))

def test_missing_authorship_proof():
    """Missing authorship_proof should produce MISSING_AUTHORSHIP_PROOF."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission")
            return
        # Remove authorship_proof
        sub.pop("authorship_proof", None)
        ok_code, _, _ = verify_authorship_proof(sub)
        if not ok_code:
            ok("missing authorship_proof detected")
        else:
            fail("missing authorship_proof not detected")

def test_tampered_draft():
    """Tampered draft after signing should fail verification."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission")
            return
        # Tamper with the draft
        sub["record_draft"]["record_type"] = "tampered"
        ok_val, code, msg = verify_authorship_proof(sub)
        if not ok_val and ("PAYLOAD_SHA_MISMATCH" in (code or "") or "SIGNATURE" in (code or "")):
            ok(f"tampered draft detected: {code}")
        else:
            fail("tampered draft not detected")

def test_guardian_key_mismatch():
    """Guardian key mismatch should fail."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission")
            return
        # Simulate guardian key mismatch
        sub["record_draft"]["record_type"] = "guardian_application"
        sub["record_draft"]["guardian_application_content"] = {
            "guardian_public_key_sha256": "0" * 64
        }
        ok_val, code, msg = verify_authorship_proof(sub)
        if not ok_val:
            ok(f"guardian key mismatch detected: {code}")
        else:
            fail("guardian key mismatch not detected")

def test_participant_key_mismatch():
    """Participant key mismatch should fail."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission")
            return
        sub["record_draft"]["submitting_participant_identity"]["participant_public_key_sha256"] = "0" * 64
        ok_val, code, msg = verify_authorship_proof(sub)
        if not ok_val and "PARTICIPANT_KEY_MISMATCH" in (code or ""):
            ok("participant key mismatch detected")
        else:
            fail("participant key mismatch not detected", f"code={code}")

def test_private_key_leak():
    """Private key material in submission should fail."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission")
            return
        # Inject private key material
        sub["record_draft"]["leaked"] = "BEGIN PRIVATE KEY"
        ok_val, code, msg = verify_authorship_proof(sub)
        if not ok_val and "PRIVATE_KEY_LEAK" in (code or ""):
            ok("private key leak detected")
        else:
            fail("private key leak not detected")

def main():
    print("=== Gateway Authorship Proof Contract Tests ===")
    test_valid_echo_no_authorship_diagnostics()
    test_valid_context_insufficient_no_authorship_diagnostics()
    test_missing_authorship_proof()
    test_tampered_draft()
    test_guardian_key_mismatch()
    test_participant_key_mismatch()
    test_private_key_leak()
    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
