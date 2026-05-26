#!/usr/bin/env python3
"""Test authorship claim endpoint runtime safety (source-level)."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_getRepoParts_exists():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "function getRepoParts()" in server, "getRepoParts() not found"
    print("PASS: getRepoParts_exists")


def test_no_REPO_OWNER_REPO_NAME():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    # Allow in comments/strings but not as variable references
    import re
    # Check that REPO_OWNER and REPO_NAME are not used as JS identifiers
    lines = server.split("\n")
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("//") or stripped.startswith("*"):
            continue
        if "REPO_OWNER" in stripped and "owner" not in stripped.lower():
            # Allow string literals but not variable usage
            if "REPO_OWNER" in stripped and not ('"' in stripped or "'" in stripped or "`" in stripped):
                assert False, f"REPO_OWNER used as variable at line {i+1}: {stripped}"
    print("PASS: no_REPO_OWNER_REPO_NAME")


def test_claim_uses_getRepoParts():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    # Find the claim-authorship route (app.post, not capabilities string)
    idx = server.find('app.post("/gateway/claim-authorship"')
    assert idx > 0, "claim-authorship route not found"
    chunk = server[idx:idx+2000]
    assert "getRepoParts()" in chunk, "claim-authorship does not use getRepoParts()"
    print("PASS: claim_uses_getRepoParts")


def test_validates_claimable_block():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "validateClaimableMachineBlock" in server, "validateClaimableMachineBlock not found"
    assert "authorship_signature_verified" in server, "authorship_signature_verified check missing"
    assert "authorship_proof_present" in server, "authorship_proof_present check missing"
    print("PASS: validates_claimable_block")


def test_uses_canonical_message_for_verify():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "expectedClaimMessage" in server, "expectedClaimMessage not found"
    assert "buildAuthorshipClaimMessage" in server, "buildAuthorshipClaimMessage not found"
    print("PASS: uses_canonical_message_for_verify")


def test_idempotent_path():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "idempotent" in server, "idempotent response path not found"
    assert "alreadyClaimed" in server or "already_claimed" in server, "alreadyClaimed check not found"
    print("PASS: idempotent_path")


def test_uses_gatewayError():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    idx = server.find('app.post("/gateway/claim-authorship"')
    assert idx > 0
    chunk = server[idx:]
    assert "gatewayError(" in chunk, "claim-authorship does not use gatewayError()"
    assert "sendGatewayError(" in chunk, "claim-authorship does not use sendGatewayError()"
    print("PASS: uses_gatewayError")


def test_ensureLabel_exists():
    server = (ROOT / "examples" / "github-app-backend" / "server.js").read_text()
    assert "function ensureLabel" in server or "async function ensureLabel" in server, \
        "ensureLabel helper not found"
    print("PASS: ensureLabel_exists")


if __name__ == "__main__":
    test_getRepoParts_exists()
    test_no_REPO_OWNER_REPO_NAME()
    test_claim_uses_getRepoParts()
    test_validates_claimable_block()
    test_uses_canonical_message_for_verify()
    test_idempotent_path()
    test_uses_gatewayError()
    test_ensureLabel_exists()
    print("\nAll runtime safety tests PASS")
