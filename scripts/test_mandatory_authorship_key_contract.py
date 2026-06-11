#!/usr/bin/env python3
"""test_mandatory_authorship_key_contract.py

Tests that the builder enforces mandatory Ed25519 authorship keys
for all public submission build commands, including context-insufficient.
"""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUILDER = ROOT / "downloads" / "record-chain-builder.mjs"

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
    global PASS
    PASS += 1
    print(f"  PASS: {msg}")

def fail(msg, detail=""):
    global FAIL
    FAIL += 1
    print(f"  FAIL: {msg}")
    if detail:
        print(f"        {detail}")

def run_builder(args, expect_exit=0):
    result = subprocess.run(
        ["node", str(BUILDER)] + args,
        capture_output=True, text=True, cwd=str(ROOT), timeout=30
    )
    if expect_exit is not None and result.returncode != expect_exit:
        fail(f"expected exit {expect_exit}, got {result.returncode}", result.stderr[:500])
    return result

def get_oath(record_type):
    r = subprocess.run(
        ["node", str(BUILDER), "print-oath", "--record-type", record_type],
        capture_output=True, text=True, cwd=str(ROOT), timeout=10,
    )
    return r.stdout if r.returncode == 0 else ""

def test_context_insufficient_no_keydir_succeeds():
    """context-insufficient without --key-dir should succeed (key not required)."""
    with tempfile.TemporaryDirectory() as td:
        r = run_builder([
            "context-insufficient",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--out", str(Path(td) / "out.json"),
        ], expect_exit=0)
        if r.returncode == 0:
            ok("context-insufficient without --key-dir succeeds (key not required)")
        else:
            fail("context-insufficient without --key-dir should succeed", r.stderr[:300])

def test_echo_no_keydir_fails():
    """echo without --key-dir should fail."""
    with tempfile.TemporaryDirectory() as td:
        body = Path(td) / "echo.md"
        body.write_text("Test echo body for mandatory key test.")
        oath = get_oath("echo")
        r = run_builder([
            "echo",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--body-file", str(body),
            *ECHO_CTX,
            "--readback", oath,
            "--out", str(Path(td) / "out.json"),
        ], expect_exit=1)
        if "--key-dir is required" in r.stderr:
            ok("echo without --key-dir fails with clear message")
        else:
            fail("echo without --key-dir", r.stderr[:300])

def test_keydir_generates_keypair():
    """--key-dir with no existing keypair should auto-generate."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        body = Path(td) / "echo.md"
        body.write_text("Test echo body.")
        oath = get_oath("echo")
        run_builder([
            "echo",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--body-file", str(body),
            *ECHO_CTX,
            "--readback", oath,
            "--key-dir", str(key_dir),
            "--out", str(Path(td) / "out.json"),
        ], expect_exit=None)
        if (key_dir / "authorship-private.pem").exists():
            ok("auto-generates authorship-private.pem")
        else:
            fail("auto-generates authorship-private.pem")
        if (key_dir / "authorship-public.pem").exists():
            ok("auto-generates authorship-public.pem")
        else:
            fail("auto-generates authorship-public.pem")

def test_private_key_mode_0600():
    """Private key file should have mode 0o600."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        body = Path(td) / "echo.md"
        body.write_text("Test echo body.")
        oath = get_oath("echo")
        run_builder([
            "echo",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--body-file", str(body),
            *ECHO_CTX,
            "--readback", oath,
            "--key-dir", str(key_dir),
            "--out", str(Path(td) / "out.json"),
        ], expect_exit=None)
        priv = key_dir / "authorship-private.pem"
        if priv.exists():
            mode = oct(priv.stat().st_mode & 0o777)
            if mode == "0o600":
                ok("private key mode is 0600")
            else:
                fail(f"private key mode is {mode}, expected 0o600")

def test_custody_warning_written():
    """AUTHORSHIP_KEY_CUSTODY_WARNING.txt should be written."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        body = Path(td) / "echo.md"
        body.write_text("Test echo body.")
        oath = get_oath("echo")
        run_builder([
            "echo",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--body-file", str(body),
            *ECHO_CTX,
            "--readback", oath,
            "--key-dir", str(key_dir),
            "--out", str(Path(td) / "out.json"),
        ], expect_exit=None)
        if (key_dir / "AUTHORSHIP_KEY_CUSTODY_WARNING.txt").exists():
            ok("custody warning file written")
        else:
            fail("custody warning file not written")

def test_public_summary_written():
    """authorship-public-summary.json should be written."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        body = Path(td) / "echo.md"
        body.write_text("Test echo body.")
        oath = get_oath("echo")
        run_builder([
            "echo",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--body-file", str(body),
            *ECHO_CTX,
            "--readback", oath,
            "--key-dir", str(key_dir),
            "--out", str(Path(td) / "out.json"),
        ], expect_exit=None)
        summary = key_dir / "authorship-public-summary.json"
        if summary.exists():
            data = json.loads(summary.read_text())
            if data.get("schema") == "trinityaccord.authorship-key-public-summary.v1":
                ok("authorship-public-summary.json written with correct schema")
            else:
                fail("authorship-public-summary.json schema mismatch")
        else:
            fail("authorship-public-summary.json not written")

def test_echo_has_authorship_proof():
    """echo submission should have authorship_proof."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        body = Path(td) / "echo.md"
        body.write_text("Test echo body.")
        out = Path(td) / "out.json"
        oath = get_oath("echo")
        run_builder([
            "echo",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--body-file", str(body),
            *ECHO_CTX,
            "--readback", oath,
            "--key-dir", str(key_dir),
            "--out", str(out),
        ], expect_exit=None)
        if out.exists():
            sub = json.loads(out.read_text())
            proof = sub.get("authorship_proof")
            if isinstance(proof, dict) and proof.get("algorithm") == "ed25519":
                ok("echo has Ed25519 authorship_proof")
            else:
                fail("echo missing or invalid authorship_proof")
        else:
            fail("echo output file not created")

def test_context_insufficient_no_authorship_proof():
    """context-insufficient does not require authorship key, so no authorship_proof."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "out.json"
        run_builder([
            "context-insufficient",
            "--actor-label", "Test Agent",
            "--provider", "Test Runtime",
            "--out", str(out),
        ], expect_exit=0)
        if out.exists():
            sub = json.loads(out.read_text())
            proof = sub.get("authorship_proof")
            if proof is None:
                ok("context-insufficient has no authorship_proof (key not required)")
            else:
                # If proof exists, it should be valid
                if isinstance(proof, dict) and proof.get("algorithm") == "ed25519":
                    ok("context-insufficient has Ed25519 authorship_proof (optional)")
                else:
                    fail("context-insufficient has invalid authorship_proof")
        else:
            fail("context-insufficient output file not created")

def test_same_keydir_reuses_key():
    """Two builds with same --key-dir should reuse the same public key."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        body = Path(td) / "echo.md"
        body.write_text("Test echo body.")
        out1 = Path(td) / "out1.json"
        out2 = Path(td) / "out2.json"
        oath = get_oath("echo")
        ctx = ["--context-level", "CC-3", "--context-sufficient-for-selected-action", "true",
               "--loaded-urls", "https://www.trinityaccord.org/", "--discovery-mode", "user_task_context",
               "--record-decision", "human", "--submission-executor", "self", "--human-operator-involved", "true"]
        run_builder([
            "echo", "--actor-label", "A1", "--provider", "R1",
            "--body-file", str(body), *ctx,
            "--readback", oath, "--key-dir", str(key_dir), "--out", str(out1),
        ], expect_exit=None)
        run_builder([
            "echo", "--actor-label", "A2", "--provider", "R2",
            "--body-file", str(body), *ctx,
            "--readback", oath, "--key-dir", str(key_dir), "--out", str(out2),
        ], expect_exit=None)
        if out1.exists() and out2.exists():
            s1 = json.loads(out1.read_text())
            s2 = json.loads(out2.read_text())
            sha1 = s1.get("authorship_proof", {}).get("public_key_sha256")
            sha2 = s2.get("authorship_proof", {}).get("public_key_sha256")
            if sha1 and sha1 == sha2:
                ok("same key-dir reuses same public key SHA-256")
            else:
                fail("same key-dir produces different keys")
        else:
            fail("output files not created")

def test_no_private_key_leak():
    """Submission JSON should not contain private key material."""
    with tempfile.TemporaryDirectory() as td:
        key_dir = Path(td) / "keys"
        body = Path(td) / "echo.md"
        body.write_text("Test echo body.")
        out = Path(td) / "out.json"
        oath = get_oath("echo")
        run_builder([
            "echo", "--actor-label", "Test", "--provider", "Test",
            "--body-file", str(body), *ECHO_CTX,
            "--readback", oath, "--key-dir", str(key_dir), "--out", str(out),
        ], expect_exit=None)
        if out.exists():
            raw = out.read_text()
            if "BEGIN PRIVATE KEY" not in raw and "authorship-private.pem" not in raw:
                ok("no private key material in submission")
            else:
                fail("private key material leaked into submission")
        else:
            fail("output file not created")

def main():
    print("=== Mandatory Authorship Key Contract Tests ===")
    test_echo_no_keydir_fails()
    test_context_insufficient_no_keydir_succeeds()
    test_keydir_generates_keypair()
    test_private_key_mode_0600()
    test_custody_warning_written()
    test_public_summary_written()
    test_echo_has_authorship_proof()
    test_context_insufficient_no_authorship_proof()
    test_same_keydir_reuses_key()
    test_no_private_key_leak()
    print(f"\n=== Results: {PASS} passed, {FAIL} failed ===")
    return 1 if FAIL > 0 else 0

if __name__ == "__main__":
    sys.exit(main())
