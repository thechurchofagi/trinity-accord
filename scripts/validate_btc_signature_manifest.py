#!/usr/bin/env python3
"""Validate btc-signature.json schema + authority cross-check."""
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    errors = []
    bs = data.get("bitcoin_signature")
    if not bs:
        errors.append("missing bitcoin_signature object")
        return errors

    # method
    if bs.get("method") != "bip340-taproot-xonly":
        errors.append(f"invalid method: {bs.get('method')}")

    # address
    addr = bs.get("address", "")
    if not re.match(r"^bc1p[a-z0-9]{58,90}$", addr):
        errors.append(f"invalid address format: {addr}")

    # message_sha256
    msg = bs.get("message_sha256", "")
    if not re.match(r"^[a-fA-F0-9]{64}$", msg):
        errors.append(f"invalid message_sha256 format: {msg}")

    # pubkey_xonly
    pk = bs.get("pubkey_xonly", "")
    if not re.match(r"^[a-fA-F0-9]{64}$", pk):
        errors.append(f"invalid pubkey_xonly format: {pk}")

    # signature
    sig = bs.get("signature", "")
    if not re.match(r"^[a-fA-F0-9]{128}$", sig):
        errors.append(f"invalid signature format: {sig}")

    # boundary
    boundary = bs.get("boundary", "")
    if not boundary:
        errors.append("boundary is empty")

    return errors


def cross_check_authority(data):
    """Cross-check BTC address and message_sha256 against authority manifest."""
    errors = []
    bs = data.get("bitcoin_signature", {})

    auth_path = ROOT / "archive" / "authority-manifest" / "authority.jcs.json"
    if not auth_path.exists():
        errors.append(f"authority manifest not found: {auth_path}")
        return errors

    auth_text = auth_path.read_text(encoding="utf-8")
    auth = json.loads(auth_text)

    # Address cross-check
    auth_btc = auth.get("guardian", {}).get("btc_minter_address", "")
    sig_btc = bs.get("address", "")
    if sig_btc != auth_btc:
        errors.append(f"BTC address mismatch: signature={sig_btc} authority={auth_btc}")

    # message_sha256 cross-check (should be sha256 of authority.jcs.json bytes)
    auth_sha256 = hashlib.sha256(auth_text.encode("utf-8")).hexdigest()
    sig_msg = bs.get("message_sha256", "").lower()
    if sig_msg != auth_sha256:
        errors.append(f"message_sha256 mismatch: signature={sig_msg} authority_sha256={auth_sha256}")

    return errors


def self_test():
    print("Running BTC signature validator self-test...")

    valid = {
        "bitcoin_signature": {
            "method": "bip340-taproot-xonly",
            "address": "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf",
            "message_sha256": "a" * 64,
            "pubkey_xonly": "b" * 64,
            "signature": "c" * 128,
            "boundary": "non-amending"
        }
    }
    errs = validate(valid)
    assert not errs, f"valid should pass: {errs}"

    # Bad method
    bad_method = {"bitcoin_signature": dict(valid["bitcoin_signature"], method="bad")}
    errs = validate(bad_method)
    assert any("method" in e for e in errs), f"should reject bad method: {errs}"

    # Bad address
    bad_addr = {"bitcoin_signature": dict(valid["bitcoin_signature"], address="bad")}
    errs = validate(bad_addr)
    assert any("address" in e for e in errs), f"should reject bad address: {errs}"

    # Bad message_sha256
    bad_msg = {"bitcoin_signature": dict(valid["bitcoin_signature"], message_sha256="xyz")}
    errs = validate(bad_msg)
    assert any("message_sha256" in e for e in errs), f"should reject bad message_sha256: {errs}"

    # Bad pubkey
    bad_pk = {"bitcoin_signature": dict(valid["bitcoin_signature"], pubkey_xonly="xyz")}
    errs = validate(bad_pk)
    assert any("pubkey_xonly" in e for e in errs), f"should reject bad pubkey: {errs}"

    # Bad signature length
    bad_sig = {"bitcoin_signature": dict(valid["bitcoin_signature"], signature="abc")}
    errs = validate(bad_sig)
    assert any("signature" in e for e in errs), f"should reject bad signature: {errs}"

    # Missing bitcoin_signature
    errs = validate({})
    assert any("bitcoin_signature" in e for e in errs), f"should reject missing bitcoin_signature: {errs}"

    print("PASS: BTC signature validator self-test")
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_btc_signature_manifest.py [--self-test|<path>]")
        return 1

    if sys.argv[1] == "--self-test":
        return self_test()

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"FAIL: file not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    errors = validate(data)

    if errors:
        print(f"FAIL: {len(errors)} schema error(s):")
        for e in errors:
            print(f"  - {e}")
        return 1

    # Cross-check authority
    xerrors = cross_check_authority(data)
    if xerrors:
        print(f"FAIL: {len(xerrors)} authority cross-check error(s):")
        for e in xerrors:
            print(f"  - {e}")
        return 1

    print(f"PASS: {path} (schema + authority cross-check)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
