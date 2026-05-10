#!/usr/bin/env python3
"""Validate authority.jcs.json against schema and authority cross-checks."""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def stable_json(value):
    """JCS-like canonical JSON serialization."""
    if value is None or isinstance(value, (bool, int, float, str)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    if isinstance(value, list):
        return "[" + ",".join(stable_json(x) for x in value) + "]"
    if isinstance(value, dict):
        return "{" + ",".join(
            json.dumps(k, ensure_ascii=False, separators=(",", ":")) + ":" + stable_json(value[k])
            for k in sorted(value.keys())
        ) + "}"
    raise TypeError(type(value))


def validate(data, file_text=None):
    errors = []

    # Required top-level keys
    for key in ("guardian", "bitcoin", "ethereum", "boundary"):
        if key not in data:
            errors.append(f"missing required top-level key: {key}")

    guardian = data.get("guardian", {})

    # Guardian required fields
    for field in ("name", "role", "btc_minter_address", "eth_address", "ar_owner"):
        if not guardian.get(field):
            errors.append(f"guardian.{field} is missing or empty")

    # BTC address format
    btc_addr = guardian.get("btc_minter_address", "")
    if btc_addr and not re.match(r"^bc1p[a-z0-9]{58,90}$", btc_addr):
        errors.append(f"guardian.btc_minter_address invalid format: {btc_addr}")

    # ETH address format
    eth_addr = guardian.get("eth_address", "")
    if eth_addr and not re.match(r"^0x[a-fA-F0-9]{40}$", eth_addr):
        errors.append(f"guardian.eth_address invalid format: {eth_addr}")

    # ar_owner non-empty
    ar_owner = guardian.get("ar_owner", "")
    if ar_owner and len(ar_owner) < 20:
        errors.append(f"guardian.ar_owner too short: {ar_owner}")

    # boundary
    boundary = data.get("boundary", "")
    if not boundary:
        errors.append("boundary is empty")

    # bitcoin.originals should exist and be non-empty
    bitcoin = data.get("bitcoin", {})
    originals = bitcoin.get("originals")
    if originals is not None and len(originals) == 0:
        errors.append("bitcoin.originals is empty array")

    # ethereum.attestations should exist and be non-empty
    ethereum = data.get("ethereum", {})
    attestations = ethereum.get("attestations")
    if attestations is not None and len(attestations) == 0:
        errors.append("ethereum.attestations is empty array")

    # JCS canonicalization check
    if file_text is not None:
        canonical = stable_json(data)
        # Strip trailing newline for comparison
        normalized_text = file_text.rstrip("\n")
        if canonical != normalized_text:
            errors.append("file is not JCS canonical (key order or formatting differs)")

    return errors


def self_test():
    """Run self-test with synthetic data."""
    print("Running authority manifest validator self-test...")

    # Valid minimal
    minimal = {
        "guardian": {
            "name": "Test",
            "role": "Guardian",
            "btc_minter_address": "bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf",
            "eth_address": "0xbc63566A41cBfDB9C266a5941CBe47894DaA54A8",
            "ar_owner": "8Y8GRimuESN_u8tJihCd5nywb-X-lJ_2vWqFAfHeQIE"
        },
        "bitcoin": {"originals": [{"txid": "abc"}]},
        "ethereum": {"attestations": [{"tx_hash": "0x123"}], "chainId": 1},
        "boundary": "non-amending"
    }
    errs = validate(minimal)
    assert not errs, f"valid minimal should pass: {errs}"

    # Missing guardian
    no_guardian = {"bitcoin": {}, "ethereum": {}, "boundary": "x"}
    errs = validate(no_guardian)
    assert any("guardian" in e for e in errs), f"should reject missing guardian: {errs}"

    # Bad BTC address
    bad_btc = dict(minimal, guardian=dict(minimal["guardian"], btc_minter_address="bad"))
    errs = validate(bad_btc)
    assert any("btc_minter_address" in e for e in errs), f"should reject bad BTC addr: {errs}"

    # Bad ETH address
    bad_eth = dict(minimal, guardian=dict(minimal["guardian"], eth_address="bad"))
    errs = validate(bad_eth)
    assert any("eth_address" in e for e in errs), f"should reject bad ETH addr: {errs}"

    # Empty boundary
    bad_boundary = dict(minimal, boundary="")
    errs = validate(bad_boundary)
    assert any("boundary" in e for e in errs), f"should reject empty boundary: {errs}"

    # Non-canonical key order
    import copy
    noncanon = copy.deepcopy(minimal)
    noncanon_text = json.dumps(noncanon, indent=2, sort_keys=True)
    errs = validate(noncanon, noncanon_text)
    assert any("canonical" in e for e in errs), f"should reject non-canonical: {errs}"

    print("PASS: authority manifest validator self-test")
    return 0


def main():
    if len(sys.argv) < 2:
        print("Usage: validate_authority_manifest.py [--self-test|<path>]")
        return 1

    if sys.argv[1] == "--self-test":
        return self_test()

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"FAIL: file not found: {path}")
        return 1

    text = path.read_text(encoding="utf-8")
    data = json.loads(text)
    errors = validate(data, file_text=text)

    if errors:
        print(f"FAIL: {len(errors)} error(s) in {path}:")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(f"PASS: {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
