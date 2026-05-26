#!/usr/bin/env python3
"""
Test: NFT CAR tmp/cache safety (TA-REDTEAM-2026-005-B)

Validates that:
- Cached files are verified against expected hash/size before acceptance
- TMP_DIR is unique (mkdtempSync) or cleaned on start
- Packaging only uses verifiedCarFiles, not full TMP_DIR scan
"""

import sys
import os

SCRIPT = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'download-nft-cars.mjs')


def read_script():
    with open(SCRIPT, 'r') as f:
        return f.read()


def test_cached_path_verifies():
    """Cache hit path must call verifyDownloadedCarBuffer."""
    src = read_script()
    # Look for cache block: exists + size > 0 -> verifyDownloadedCarBuffer
    lines = src.split('\n')
    in_cache_block = False
    found_verify = False
    for i, line in enumerate(lines):
        if 'existsSync(dest)' in line and 'statSync(dest).size > 0' in line:
            in_cache_block = True
        if in_cache_block and 'verifyDownloadedCarBuffer' in line:
            found_verify = True
            break
        if in_cache_block and ('return;' in line or 'downloadTxid' in line):
            break
    assert found_verify, "Cache path does not call verifyDownloadedCarBuffer"
    print("  ✓ cached path uses verifyDownloadedCarBuffer")


def test_stale_cache_deleted_on_mismatch():
    """Cache mismatch must delete the stale file before re-downloading."""
    src = read_script()
    assert 'rmSync(dest' in src, "Missing fs.rmSync for stale cache cleanup"
    # The rmSync should be in the catch block after verify fails
    lines = src.split('\n')
    in_cache_catch = False
    found_rm_after_catch = False
    for i, line in enumerate(lines):
        if 'Stale or corrupted cache' in line or ('catch' in line and i > 0 and 'verifyDownloadedCarBuffer' in '\n'.join(lines[max(0,i-10):i])):
            in_cache_catch = True
        if in_cache_catch and 'rmSync' in line:
            found_rm_after_catch = True
            break
    assert found_rm_after_catch, "rmSync not found in catch block for stale cache"
    print("  ✓ stale cache deleted on mismatch")


def test_tmp_dir_unique_or_cleaned():
    """TMP_DIR uses mkdtempSync (unique) or explicit dir is cleaned on start."""
    src = read_script()
    has_mktemp = 'mkdtempSync' in src
    has_clean = 'rmSync' in src and 'recursive' in src
    assert has_mktemp or has_clean, "TMP_DIR is neither unique nor cleaned on start"
    if has_mktemp:
        print("  ✓ TMP_DIR uses mkdtempSync (unique)")
    if has_clean:
        print("  ✓ explicit TMP_DIR is cleaned on start")


def test_packaging_uses_verified_list():
    """Packaging uses verifiedCarFiles, not fs.readdirSync(TMP_DIR)."""
    src = read_script()
    # Should NOT scan TMP_DIR for .car files
    assert 'readdirSync(TMP_DIR)' not in src or '.car' not in src.split('readdirSync(TMP_DIR)')[1][:50] if 'readdirSync(TMP_DIR)' in src else True, \
      "Packaging still scans TMP_DIR for .car files"
    # Should use verifiedCarFiles
    assert 'verifiedCarFiles' in src, "Missing verifiedCarFiles list"
    print("  ✓ packaging uses verifiedCarFiles")


def test_verified_car_files_count_check():
    """verifiedCarFiles.length must equal txids.size before packaging."""
    src = read_script()
    assert 'verifiedCarFiles.length !== txids.size' in src, \
      "Missing count check: verifiedCarFiles vs txids.size"
    print("  ✓ verified count check present")


def main():
    print("Running download-nft-cars tmp/cache safety tests...")
    test_cached_path_verifies()
    test_stale_cache_deleted_on_mismatch()
    test_tmp_dir_unique_or_cleaned()
    test_packaging_uses_verified_list()
    test_verified_car_files_count_check()
    print("\nDOWNLOAD_NFT_CARS_TMP_CACHE_SAFETY_OK")


if __name__ == '__main__':
    main()
