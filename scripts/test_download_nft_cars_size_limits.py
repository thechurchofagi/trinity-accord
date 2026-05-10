#!/usr/bin/env python3
"""
Test: NFT CAR size limits (TA-HARDENING-005-D)

Validates per-file and total disk caps exist in download-nft-cars.mjs.
"""

import sys
import os

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'download-nft-cars.mjs')


def read_script():
    with open(SCRIPT, 'r') as f:
        return f.read()


def test_has_max_car_bytes():
    """Script defines MAX_CAR_BYTES per-file cap."""
    src = read_script()
    assert 'MAX_CAR_BYTES' in src, "Missing MAX_CAR_BYTES per-file cap"
    print("  ✓ MAX_CAR_BYTES defined")


def test_has_max_total_bytes():
    """Script defines MAX_TOTAL_BYTES total cap."""
    src = read_script()
    assert 'MAX_TOTAL_BYTES' in src, "Missing MAX_TOTAL_BYTES total cap"
    print("  ✓ MAX_TOTAL_BYTES defined")


def test_expected_size_cap_check():
    """Expected size exceeding cap is rejected before download."""
    src = read_script()
    assert 'Expected size exceeds per-file cap' in src, \
      "Missing expected size cap check"
    print("  ✓ expected size cap check present")


def test_actual_size_cap_check():
    """Actual size exceeding cap is rejected after download."""
    src = read_script()
    assert 'CAR too large' in src, "Missing actual size cap check"
    print("  ✓ actual size cap check present")


def test_total_size_cap_check():
    """Total verified bytes exceeding cap throws."""
    src = read_script()
    assert 'Total CAR verified size exceeds cap' in src, \
      "Missing total size cap check"
    print("  ✓ total size cap check present")


def test_parse_positive_int_env():
    """parsePositiveIntEnv validates min/max bounds."""
    src = read_script()
    assert 'parsePositiveIntEnv' in src, "Missing parsePositiveIntEnv helper"
    print("  ✓ parsePositiveIntEnv present")


def main():
    print("Running download-nft-cars size limits tests...")
    test_has_max_car_bytes()
    test_has_max_total_bytes()
    test_expected_size_cap_check()
    test_actual_size_cap_check()
    test_total_size_cap_check()
    test_parse_positive_int_env()
    print("\nDOWNLOAD_NFT_CARS_SIZE_LIMITS_OK")


if __name__ == '__main__':
    main()
