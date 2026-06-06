#!/usr/bin/env python3
"""test_gateway_authorship_proof_contract.py

Tests that the gateway correctly verifies Ed25519 authorship proofs.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"

sys.path.insert(0, str(ROOT / "apps/record_chain_intake_gateway"))
from gateway.authorship import verify_authorship_proof_submission

PASS = 0
FAIL = 0

ECHO_CTX = [
    "--context-level", "CC-3",
    "--context-sufficient-for-selected-action", "true",
    "--loaded-urls", "https://www.trinityaccord.org/",
    "--discovery-mode", "user_task_context",
    "--record-decision", "human",
    "--submission-executor", "self",
    "--human-operator-involved", "true",
]

def ok(msg):
    global PASS; PASS += 1; print(f"  PASS: {msg}")

def fail(msg, detail=""):
    global FAIL; FAIL += 1; print(f"  FAIL: {msg}")
    if detail: print(f"        {detail}")

def get_oath(record_type):
    r = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", record_type],
        capture_output=True, text=True, cwd=str(ROOT), timeout=10,
    )
    return r.stdout if r.returncode == 0 else ""

def build_echo_submission(key_dir):
    with tempfile.TemporaryDirectory() as td:
        body = Path(td) / "echo.md"
        body.write_text("Test echo for gateway verification.")
        out = Path(td) / "out.json"
        oath = get_oath("echo")
        subprocess.run(
            ["node", str(BUILDER), "echo",
             "--actor-label", "Test Agent", "--provider", "Test Runtime",
             "--body-file", str(body), *ECHO_CTX,
             "--readback", oath, "--key-dir", str(key_dir), "--out", str(out)],
            capture_output=True, text=True, cwd=str(ROOT), timeout=30
        )
        if out.exists():
            return json.loads(out.read_text())
    return None

def build_context_insufficient_submission(key_dir):
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        subprocess.run(
            ["node", str(BUILDER), "context-insufficient",
             "--actor-label", "Test Agent", "--provider", "Test Runtime",
             "--key-dir", str(key_dir), "--out", str(out)],
            capture_output=True, text=True, cwd=str(ROOT), timeout=30
        )
        if out.exists():
            return json.loads(out.read_text())
    return None

def test_valid_echo_no_authorship_diagnostics():
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission"); return
        ok_val, code, msg = verify_authorship_proof_submission(sub)
        if ok_val:
            ok("valid echo passes authorship verification")
        else:
            fail(f"valid echo failed: {code} - {msg}")

def test_valid_context_insufficient_no_authorship_diagnostics():
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_context_insufficient_submission(key_dir)
        if not sub:
            fail("could not build context-insufficient submission"); return
        ok_val, code, msg = verify_authorship_proof_submission(sub)
        if ok_val:
            ok("valid context-insufficient passes authorship verification")
        else:
            fail(f"valid context-insufficient failed: {code} - {msg}")

def test_missing_authorship_proof():
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission"); return
        sub.pop("authorship_proof", None)
        ok_val, code, msg = verify_authorship_proof_submission(sub)
        if not ok_val:
            ok("missing authorship_proof detected")
        else:
            fail("missing authorship_proof not detected")

def test_tampered_draft():
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission"); return
        sub["record_draft"]["record_type"] = "tampered"
        ok_val, code, msg = verify_authorship_proof_submission(sub)
        if not ok_val:
            ok(f"tampered draft detected: {code}")
        else:
            fail("tampered draft not detected")

def test_guardian_key_mismatch():
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission"); return
        sub["record_draft"]["record_type"] = "guardian_application"
        sub["record_draft"]["guardian_application_content"] = {
            "guardian_public_key_sha256": "0" * 64
        }
        ok_val, code, msg = verify_authorship_proof_submission(sub)
        if not ok_val:
            ok(f"guardian key mismatch detected: {code}")
        else:
            fail("guardian key mismatch not detected")

def test_participant_key_mismatch():
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission"); return
        # Tamper with the proof's public_key_sha256 to simulate key mismatch
        sub["authorship_proof"]["public_key_sha256"] = "0" * 64
        ok_val, code, msg = verify_authorship_proof_submission(sub)
        if not ok_val:
            ok(f"participant/key mismatch detected: {code}")
        else:
            fail("participant key mismatch not detected")

def test_private_key_leak():
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        sub = build_echo_submission(key_dir)
        if not sub:
            fail("could not build echo submission"); return
        # Inject private key material into the top-level submission (not draft)
        sub["leaked_field"] = "BEGIN PRIVATE KEY"
        ok_val, code, msg = verify_authorship_proof_submission(sub)
        if not ok_val and "PRIVATE_KEY_LEAK" in (code or ""):
            ok("private key leak detected")
        else:
            fail("private key leak not detected", f"code={code}")

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
