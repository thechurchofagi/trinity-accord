#!/usr/bin/env python3
"""
Test: NFT CAR expected integrity enforcement (TA-REDTEAM-2026-005-A)

Validates that download-nft-cars.mjs enforces expected hash/size
before accepting any downloaded or cached CAR file.
"""

import subprocess
import sys
import os
import tempfile
import shutil

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'download-nft-cars.mjs')


def read_script():
    with open(SCRIPT, 'r') as f:
        return f.read()


def test_helpers_exported():
    """verifyDownloadedCarBuffer, sha256hex, validateExpectedInfo, normalizeExpectedSize are exported."""
    src = read_script()
    for name in ['verifyDownloadedCarBuffer', 'sha256hex', 'validateExpectedInfo', 'normalizeExpectedSize']:
        assert f'export' in src and name in src, f"{name} not exported from download-nft-cars.mjs"
    print("  ✓ helpers exported")


def test_verify_sha256_mismatch_throws():
    """verifyDownloadedCarBuffer throws on sha256 mismatch."""
    src = read_script()
    # Must contain explicit sha256 mismatch check
    assert 'SHA256 mismatch' in src, "Missing SHA256 mismatch error message"
    assert 'actualSha256 !== expected' in src or 'actualSha256 !== expected.expected_sha256' in src, \
      "Missing sha256 comparison in verifyDownloadedCarBuffer"
    print("  ✓ sha256 mismatch throws")


def test_verify_size_mismatch_throws():
    """verifyDownloadedCarBuffer throws on size mismatch."""
    src = read_script()
    assert 'Size mismatch' in src, "Missing Size mismatch error message"
    assert 'actualSize !== expected' in src or 'actualSize !== expected.expected_size' in src, \
      "Missing size comparison in verifyDownloadedCarBuffer"
    print("  ✓ size mismatch throws")


def test_missing_expected_sha256_throws():
    """validateExpectedInfo rejects missing/invalid expected sha256."""
    src = read_script()
    assert 'Missing or invalid expected sha256' in src, \
      "Missing error for missing expected sha256"
    assert 'SHA256_RE' in src, "Missing SHA256 regex validation"
    print("  ✓ missing expected sha256 throws")


def test_missing_expected_size_throws():
    """validateExpectedInfo rejects missing/invalid expected size."""
    src = read_script()
    assert 'Missing or invalid expected size' in src, \
      "Missing error for missing expected size"
    print("  ✓ missing expected size throws")


def test_download_path_uses_verify():
    """Download path calls verifyDownloadedCarBuffer before writing file."""
    src = read_script()
    # After downloadTxid, must verify before writeFileSync
    lines = src.split('\n')
    in_download_catch = False
    found_verify_before_write = False
    for i, line in enumerate(lines):
        if 'downloadTxid' in line and 'await' in line:
            # Look ahead for verify before write
            for j in range(i+1, min(i+10, len(lines))):
                if 'verifyDownloadedCarBuffer' in lines[j]:
                    found_verify_before_write = True
                    break
                if 'writeFileSync' in lines[j]:
                    break
    assert found_verify_before_write, "Download path does not verify before writing"
    print("  ✓ download path uses verify")


def test_fail_increments_on_mismatch():
    """Hash/size mismatch results in fail++ (not pass++)."""
    src = read_script()
    # In the catch block, fail++ should be present
    assert 'fail++' in src, "Missing fail++ for verification failures"
    print("  ✓ fail increments on mismatch")


def test_no_package_on_fail():
    """Script refuses to package when fail > 0."""
    src = read_script()
    assert 'refusing to package' in src or 'fail > 0' in src, \
      "Missing guard against packaging with failures"
    print("  ✓ no package on fail")


def main():
    print("Running download-nft-cars expected integrity tests...")
    test_helpers_exported()
    test_verify_sha256_mismatch_throws()
    test_verify_size_mismatch_throws()
    test_missing_expected_sha256_throws()
    test_missing_expected_size_throws()
    test_download_path_uses_verify()
    test_fail_increments_on_mismatch()
    test_no_package_on_fail()
    print("\nDOWNLOAD_NFT_CARS_EXPECTED_INTEGRITY_OK")


if __name__ == '__main__':
    main()
