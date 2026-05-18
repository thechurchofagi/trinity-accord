#!/usr/bin/env python3
"""Test that Python and JS authorship claim helpers agree."""
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_python_js_agree():
    """Build message with Python, sign with JS, verify with Node crypto."""
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Generate keypair
        subprocess.check_call(
            ["node", str(ROOT / "scripts" / "generate_agent_authorship_keypair.mjs"), str(tmpdir / "testkey")],
            cwd=str(ROOT)
        )

        # Build message with Python
        subprocess.check_call([
            sys.executable,
            str(ROOT / "scripts" / "build_agent_authorship_claim_message.py"),
            "--issue-number", "999",
            "--repo", "thechurchofagi/trinity-accord",
            "--public-key-sha256", "a" * 64,
            "--payload-sha256", "b" * 64,
            "--out", str(tmpdir / "message.txt")
        ])

        # Sign with JS
        subprocess.check_call([
            "node",
            str(ROOT / "scripts" / "sign_agent_authorship_claim.mjs"),
            "--message", str(tmpdir / "message.txt"),
            "--private-key", str(tmpdir / "testkey.private.pem"),
            "--out", str(tmpdir / "signature.txt")
        ])

        # Build request
        subprocess.check_call([
            "node",
            str(ROOT / "scripts" / "build_agent_authorship_claim_request.mjs"),
            "--issue-number", "999",
            "--public-key", str(tmpdir / "testkey.public.pem"),
            "--message", str(tmpdir / "message.txt"),
            "--signature", str(tmpdir / "signature.txt"),
            "--out", str(tmpdir / "request.json"),
            "--claimant-note", "test claim"
        ])

        # Validate request JSON
        req = json.loads((tmpdir / "request.json").read_text())
        assert req["issue_number"] == 999
        assert "public_key_pem" in req
        assert "claim_message" in req
        assert "signature_base64" in req
        assert "private" not in json.dumps(req).lower(), "private key leaked in request!"

        # Verify signature with Node crypto
        verify_script = tmpdir / "verify.mjs"
        verify_script.write_text(f"""
import {{ verify }} from "node:crypto";
import {{ readFileSync }} from "node:fs";

const msg = readFileSync("{tmpdir}/message.txt", "utf8").trimEnd();
const sig = readFileSync("{tmpdir}/signature.txt", "utf8").trim();
const pubKey = readFileSync("{tmpdir}/testkey.public.pem", "utf8");

const ok = verify(null, Buffer.from(msg, "utf8"), pubKey, Buffer.from(sig, "base64"));
console.log(ok ? "VERIFY_OK" : "VERIFY_FAIL");
process.exit(ok ? 0 : 1);
""")
        result = subprocess.check_output(
            ["node", str(verify_script)],
            cwd=str(ROOT),
            text=True
        ).strip()
        assert "VERIFY_OK" in result, f"Signature verification failed: {result}"

    print("PASS: python_js_agree")


def test_request_has_no_private_key():
    """Request JSON must never contain private key material."""
    import json

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        subprocess.check_call(
            ["node", str(ROOT / "scripts" / "generate_agent_authorship_keypair.mjs"), str(tmpdir / "testkey")],
            cwd=str(ROOT)
        )

        subprocess.check_call([
            sys.executable,
            str(ROOT / "scripts" / "build_agent_authorship_claim_message.py"),
            "--issue-number", "1",
            "--public-key-sha256", "a" * 64,
            "--payload-sha256", "b" * 64,
            "--out", str(tmpdir / "message.txt")
        ])

        subprocess.check_call([
            "node",
            str(ROOT / "scripts" / "sign_agent_authorship_claim.mjs"),
            "--message", str(tmpdir / "message.txt"),
            "--private-key", str(tmpdir / "testkey.private.pem"),
            "--out", str(tmpdir / "signature.txt")
        ])

        subprocess.check_call([
            "node",
            str(ROOT / "scripts" / "build_agent_authorship_claim_request.mjs"),
            "--issue-number", "1",
            "--public-key", str(tmpdir / "testkey.public.pem"),
            "--message", str(tmpdir / "message.txt"),
            "--signature", str(tmpdir / "signature.txt"),
            "--out", str(tmpdir / "request.json")
        ])

        req_text = (tmpdir / "request.json").read_text()
        req = json.loads(req_text)
        assert "private" not in req_text.lower(), "private key reference in request JSON"
        assert "PRIVATE" not in req_text, "PRIVATE key reference in request JSON"

    print("PASS: request_has_no_private_key")


if __name__ == "__main__":
    test_python_js_agree()
    test_request_has_no_private_key()
    print("\nAll claim message helper tests PASS")
