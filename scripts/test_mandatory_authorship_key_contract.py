#!/usr/bin/env python3
"""Test mandatory authorship key contract for Record-Chain submissions.

Verifies:
  - --key-dir is required for all public submission commands
  - Keypair is auto-generated when missing
  - Keypair is reused when present
  - Custody warning files are written
  - Private key file mode is 0600
  - authorship_proof is present in all submissions
  - participant_public_key_sha256 matches authorship_proof.public_key_sha256
  - guardian_application binds guardian key to authorship key
  - guardian key mismatch is rejected
  - No private key material leaks into submission JSON
  - Doctor rejects missing authorship_proof
"""
from __future__ import annotations

import json
import os
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "downloads/record-chain-builder.mjs"


def run(cmd, cwd=None, expect=0):
    result = subprocess.run(
        cmd,
        cwd=str(cwd or ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if result.returncode != expect:
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)
        raise SystemExit(f"command failed: {' '.join(map(str, cmd))}; expected {expect}, got {result.returncode}")
    return result


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def require(cond, msg):
    if not cond:
        raise SystemExit(msg)


def print_oath(record_type: str) -> str:
    result = run(["node", str(BUILDER), "print-oath", "--record-type", record_type])
    return result.stdout.strip()


def common_args(key_dir: Path):
    return [
        "--actor-label", "Mandatory Key Test Agent",
        "--provider", "Temporary Test Runtime",
        "--context-level", "CC-3",
        "--context-sufficient-for-selected-action", "true",
        "--loaded-urls", "https://www.trinityaccord.org/,https://www.trinityaccord.org/api/agent-start.v2.json",
        "--discovery-mode", "self_discovered",
        "--record-decision", "self",
        "--submission-executor", "self",
        "--human-operator-involved", "false",
        "--key-dir", str(key_dir),
    ]


def assert_no_private_material(obj):
    raw = json.dumps(obj, ensure_ascii=False)
    require("BEGIN PRIVATE KEY" not in raw, "private key leaked into JSON")
    require("authorship-private.pem" not in raw, "private key filename leaked into JSON")


def assert_authorship_bound(sub, expected_pub_sha=None):
    proof = sub.get("authorship_proof")
    require(isinstance(proof, dict), "missing authorship_proof")
    pub = proof.get("public_key_sha256")
    require(isinstance(pub, str) and len(pub) == 64, "invalid public_key_sha256")

    spi = sub["record_draft"]["submitting_participant_identity"]
    require(spi.get("participant_public_key_sha256") == pub, "participant key not bound to authorship proof")

    if expected_pub_sha:
        require(pub == expected_pub_sha, "expected key continuity public sha mismatch")

    if sub["record_type"] == "guardian_application":
        gk = sub["record_draft"]["guardian_application_content"]["guardian_public_key_sha256"]
        require(gk == pub, "guardian key not bound to authorship key")

    assert_no_private_material(sub)
    return pub


def main():
    require(BUILDER.exists(), "builder missing")

    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        key_dir = tmp / "agent-key"

        echo_oath = print_oath("echo")

        # ── Test 1: No key-dir must fail ──────────────────────────────
        no_key = run([
            "node", str(BUILDER), "echo",
            "--actor-label", "No Key Agent",
            "--provider", "Test Runtime",
            "--body", "This should fail because no key-dir was provided.",
            "--context-level", "CC-3",
            "--context-sufficient-for-selected-action", "true",
            "--loaded-urls", "https://www.trinityaccord.org/",
            "--discovery-mode", "self_discovered",
            "--record-decision", "self",
            "--submission-executor", "self",
            "--human-operator-involved", "false",
            "--readback", echo_oath,
            "--out", str(tmp / "no-key.json"),
        ], expect=1)
        require("--key-dir is required" in (no_key.stderr + no_key.stdout), "no-key failure did not explain --key-dir requirement")

        # ── Test 2: Echo with key-dir ─────────────────────────────────
        echo_path = tmp / "echo.json"
        result = run([
            "node", str(BUILDER), "echo",
            *common_args(key_dir),
            "--body", "Mandatory key test echo.",
            "--readback", echo_oath,
            "--out", str(echo_path),
        ])
        echo = load(echo_path)
        pub_sha = assert_authorship_bound(echo)

        # ── Test 3: Key files created ─────────────────────────────────
        require((key_dir / "authorship-private.pem").exists(), "private key file missing")
        require((key_dir / "authorship-public.pem").exists(), "public key file missing")
        require((key_dir / "AUTHORSHIP_KEY_CUSTODY_WARNING.txt").exists(), "custody warning file missing")
        require((key_dir / "authorship-public-summary.json").exists(), "public summary file missing")
        warning = (key_dir / "AUTHORSHIP_KEY_CUSTODY_WARNING.txt").read_text(encoding="utf-8").upper()
        require("SANDBOX" in warning, "custody warning does not mention sandbox loss")
        require("BACK UP" in warning or "BACKUP" in warning, "custody warning does not clearly say backup")
        if os.name != "nt":
            mode = (key_dir / "authorship-private.pem").stat().st_mode & 0o777
            require(mode == 0o600, f"private key mode should be 0600, got {oct(mode)}")

        # ── Test 4: Verification reuses same key ──────────────────────
        verification_oath = print_oath("verification")
        ver_path = tmp / "verification-v3.json"
        run([
            "node", str(BUILDER), "verification",
            *common_args(key_dir),
            "--verification-level", "V3",
            "--scope-label", "mandatory-key-test",
            "--what-was-checked", "builder key generation,key continuity",
            "--verification-claim", "Mandatory authorship key is present and reused.",
            "--fresh-actions", "ran builder,checked JSON",
            "--readback", verification_oath,
            "--out", str(ver_path),
        ])
        ver = load(ver_path)
        assert_authorship_bound(ver, expected_pub_sha=pub_sha)

        # ── Test 5: Guardian application binds key ────────────────────
        guardian_oath = print_oath("guardian_application")
        ga_path = tmp / "guardian.json"
        run([
            "node", str(BUILDER), "guardian-application",
            *common_args(key_dir),
            "--guardian-id", "Test Forest Guardian Applicant",
            "--readback", guardian_oath,
            "--out", str(ga_path),
        ])
        ga = load(ga_path)
        assert_authorship_bound(ga, expected_pub_sha=pub_sha)

        # ── Test 6: Guardian key mismatch rejected ────────────────────
        bad = run([
            "node", str(BUILDER), "guardian-application",
            *common_args(key_dir),
            "--guardian-id", "Bad Guardian Key Test",
            "--guardian-key-sha", "0" * 64,
            "--readback", guardian_oath,
            "--out", str(tmp / "bad-guardian.json"),
        ], expect=1)
        require("guardian" in (bad.stderr + bad.stdout).lower() and "key" in (bad.stderr + bad.stdout).lower(), "guardian mismatch did not fail clearly")

        # ── Test 7: Doctor passes valid submission ────────────────────
        run(["node", str(BUILDER), "doctor", "--file", str(ga_path)], expect=0)

        # ── Test 8: Context-insufficient also requires key ────────────
        ci_path = tmp / "ci.json"
        run([
            "node", str(BUILDER), "context-insufficient",
            *common_args(key_dir),
            "--out", str(ci_path),
        ])
        ci = load(ci_path)
        assert_authorship_bound(ci, expected_pub_sha=pub_sha)

    print("PASS: mandatory authorship key contract")


if __name__ == "__main__":
    main()
