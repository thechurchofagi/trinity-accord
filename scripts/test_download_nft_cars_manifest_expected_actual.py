#!/usr/bin/env python3
"""
Test: NFT CAR manifest expected/actual fields (TA-REDTEAM-2026-005-A/B)

Validates that manifest output distinguishes expected vs actual sha256/size,
and includes aggregate checks.
"""

import sys
import os

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'download-nft-cars.mjs')


def read_script():
    with open(SCRIPT, 'r') as f:
        return f.read()


def test_manifest_has_expected_sha256():
    """Manifest items include expected_sha256 field."""
    src = read_script()
    assert 'expected_sha256' in src, "Missing expected_sha256 in manifest"
    print("  ✓ expected_sha256 field present")


def test_manifest_has_actual_sha256():
    """Manifest items include actual_sha256 field."""
    src = read_script()
    assert 'actual_sha256' in src, "Missing actual_sha256 in manifest"
    print("  ✓ actual_sha256 field present")


def test_manifest_has_sha256_match():
    """Manifest items include sha256_match field."""
    src = read_script()
    assert 'sha256_match' in src, "Missing sha256_match in manifest"
    print("  ✓ sha256_match field present")


def test_manifest_has_expected_size():
    """Manifest items include expected_size field."""
    src = read_script()
    assert 'expected_size' in src, "Missing expected_size in manifest"
    print("  ✓ expected_size field present")


def test_manifest_has_actual_size():
    """Manifest items include actual_size field."""
    src = read_script()
    assert 'actual_size' in src, "Missing actual_size in manifest"
    print("  ✓ actual_size field present")


def test_manifest_has_size_match():
    """Manifest items include size_match field."""
    src = read_script()
    assert 'size_match' in src, "Missing size_match in manifest"
    print("  ✓ size_match field present")


def test_manifest_has_verified():
    """Manifest items include verified field."""
    src = read_script()
    assert 'verified: true' in src or 'verified: false' in src or 'verified:' in src, \
      "Missing verified field in manifest"
    print("  ✓ verified field present")


def test_aggregate_sha256_check():
    """Manifest includes aggregate sha256 check (sha256_check or all_expected_sha256_matched)."""
    src = read_script()
    has_check = 'sha256_check' in src or 'all_expected_sha256_matched' in src
    assert has_check, "Missing aggregate sha256 check in manifest"
    print("  ✓ aggregate sha256 check present")


def test_aggregate_size_check():
    """Manifest includes aggregate size check (size_check or all_expected_size_matched)."""
    src = read_script()
    has_check = 'size_check' in src or 'all_expected_size_matched' in src
    assert has_check, "Missing aggregate size check in manifest"
    print("  ✓ aggregate size check present")


def test_no_old_sha256_overwrite():
    """Old pattern `sha256: hash` in manifest.push must not exist."""
    src = read_script()
    # The old dangerous pattern was: manifest.push({ ...info, txid, sha256: hash, size: buf.length })
    assert 'sha256: hash' not in src, \
      "Old pattern 'sha256: hash' still present — expected/actual fields will be overwritten"
    print("  ✓ no old sha256 overwrite pattern")


def test_fail_item_has_verified_false():
    """Failed manifest items include verified: false."""
    src = read_script()
    # In the catch block, failed items should have verified: false
    lines = src.split('\n')
    in_catch = False
    found_verified_false = False
    for line in lines:
        if 'fail++' in line:
            in_catch = True
        if in_catch and 'verified: false' in line:
            found_verified_false = True
            break
        if in_catch and 'verified: true' in line:
            break
    assert found_verified_false, "Failed items do not have verified: false"
    print("  ✓ fail items have verified: false")


def main():
    print("Running download-nft-cars manifest expected/actual tests...")
    test_manifest_has_expected_sha256()
    test_manifest_has_actual_sha256()
    test_manifest_has_sha256_match()
    test_manifest_has_expected_size()
    test_manifest_has_actual_size()
    test_manifest_has_size_match()
    test_manifest_has_verified()
    test_aggregate_sha256_check()
    test_aggregate_size_check()
    test_no_old_sha256_overwrite()
    test_fail_item_has_verified_false()
    print("\nDOWNLOAD_NFT_CARS_MANIFEST_EXPECTED_ACTUAL_OK")


if __name__ == '__main__':
    main()
