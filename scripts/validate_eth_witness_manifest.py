#!/usr/bin/env python3
"""Validate eth-witness.json schema + authority cross-check."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    errors = []

    # Required fields
    for field in ("tx_hash", "from", "to", "chainId", "input_sha256"):
        if field not in data:
            errors.append(f"missing required field: {field}")

    # tx_hash
    tx = data.get("tx_hash", "")
    if tx and not re.match(r"^0x[a-fA-F0-9]{64}$", tx):
        errors.append(f"invalid tx_hash format: {tx}")

    # from
    frm = data.get("from", "")
    if frm and not re.match(r"^0x[a-fA-F0-9]{40}$", frm):
        errors.append(f"invalid from format: {frm}")

    # to
    to = data.get("to", "")
    if to and not re.match(r"^0x[a-fA-F0-9]{40}$", to):
        errors.append(f"invalid to format: {to}")

    # chainId must be 1
    chain_id = data.get("chainId")
    if str(chain_id) != "1":
        errors.append(f"chainId must be 1, got: {chain_id}")

    # input_sha256
    inp = data.get("input_sha256", "")
    if inp and not re.match(r"^[a-fA-F0-9]{64}$", inp):
        errors.append(f"invalid input_sha256 format: {inp}")

    # input_len
    input_len = data.get("input_len")
    if input_len is not None and (not isinstance(input_len, int) or input_len < 1):
        errors.append(f"invalid input_len: {input_len}")

    return errors


def cross_check_authority(data):
    """Cross-check ETH from/to against authority manifest."""
    errors = []

    auth_path = ROOT / "archive" / "authority-manifest" / "authority.jcs.json"
    if not auth_path.exists():
        errors.append(f"authority manifest not found: {auth_path}")
        return errors

    auth = json.loads(auth_path.read_text(encoding="utf-8"))
    auth_eth = auth.get("guardian", {}).get("eth_address", "")

    # from must match authority
    if data.get("from", "").lower() != auth_eth.lower():
        errors.append(f"from mismatch: witness={data.get('from')} authority={auth_eth}")

    # to must match authority (self-transfer pattern)
    if data.get("to", "").lower() != auth_eth.lower():
        errors.append(f"to mismatch: witness={data.get('to')} authority={auth_eth}")

    return errors


def self_test():
    print("Running ETH witness validator self-test...")

    valid = {
        "tx_hash": "0xd082a3ced27ece935d4093fb001a9ebfba42b415f78de4377c8cda55338c6420",
        "from": "0xbc63566A41cBfDB9C266a5941CBe47894DaA54A8",
        "to": "0xbc63566A41cBfDB9C266a5941CBe47894DaA54A8",
        "chainId": "1",
        "input_sha256": "a" * 64,
        "input_len": 600,
        "label": "test"
    }
    errs = validate(valid)
    assert not errs, f"valid should pass: {errs}"

    # Bad tx_hash
    bad_tx = dict(valid, tx_hash="bad")
    errs = validate(bad_tx)
    assert any("tx_hash" in e for e in errs), f"should reject bad tx_hash: {errs}"

    # Bad from
    bad_from = {**valid, "from": "bad"}
    errs = validate(bad_from)
    assert any("from" in e for e in errs), f"should reject bad from: {errs}"

    # Bad to
    bad_to = {**valid, "to": "bad"}
    errs = validate(bad_to)
    assert any("to" in e for e in errs), f"should reject bad to: {errs}"

    # Bad chainId
    bad_chain = dict(valid, chainId="5")
    errs = validate(bad_chain)
    assert any("chainId" in e for e in errs), f"should reject bad chainId: {errs}"

    # Bad input_sha256
    bad_input = dict(valid, input_sha256="xyz")
    errs = validate(bad_input)
    assert any("input_sha256" in e for e in errs), f"should reject bad input_sha256: {errs}"

    # Missing field
    missing = {k: v for k, v in valid.items() if k != "tx_hash"}
    errs = validate(missing)
    assert any("tx_hash" in e for e in errs), f"should reject missing tx_hash: {errs}"

    print("PASS: ETH witness validator self-test")
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_eth_witness_manifest.py [--self-test|<path>]")
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
