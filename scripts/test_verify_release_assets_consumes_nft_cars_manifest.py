#!/usr/bin/env python3
"""Test: verify-release-assets.mjs can normalize producer-style manifest"""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Test that normalizeReleaseManifest accepts a producer-style manifest
# with per_nft_assets (the format download-nft-cars.mjs generates)
test_code = r"""
import { normalizeReleaseManifest } from './scripts/verify-release-assets.mjs';

const m = {
  schema: 'trinity-release-manifest-v1',
  release_kind: 'nft-car-backup',
  verification_basis: 'expected_sha256_and_expected_size',
  actual_nfts: 2,
  total_car_files: 4,
  contracts: 1,
  per_nft_assets: [
    {
      nft_asset_name: 'nft-0xabc-1.tar',
      contract: '0xabc',
      token_id: '1',
      files: [
        { role: 'metadata', txid: 'txMeta1', expected_path: 'nft/metadata.car', expected_sha256: 'a'.repeat(64), expected_size: 100, expected_root_cid: 'bafyMeta1', cid_check_required: false },
        { role: 'media', txid: 'txMed1', expected_path: 'nft/media.car', expected_sha256: 'b'.repeat(64), expected_size: 200, expected_root_cid: 'bafyMed1', cid_check_required: false },
      ]
    },
    {
      nft_asset_name: 'nft-0xabc-2.tar',
      contract: '0xabc',
      token_id: '2',
      files: [
        { role: 'metadata', txid: 'txMeta2', expected_path: 'nft/metadata.car', expected_sha256: 'c'.repeat(64), expected_size: 150, expected_root_cid: 'bafyMeta2', cid_check_required: false },
        { role: 'media', txid: 'txMed2', expected_path: 'nft/media.car', expected_sha256: 'd'.repeat(64), expected_size: 250, expected_root_cid: 'bafyMed2', cid_check_required: false },
      ]
    }
  ],
  does_not_prove: ['CID/root/DAG correctness unless cid_check_enabled is true'],
};

const n = normalizeReleaseManifest(m);

if (n.schema !== 'trinity-release-manifest-v1') throw new Error('schema mismatch');
if (n.expected_release_assets.length !== 2) throw new Error('expected 2 assets, got ' + n.expected_release_assets.length);
if (n.expected_asset_count !== 2) throw new Error('expected_asset_count mismatch');
if (n.expected_car_count !== 4) throw new Error('expected_car_count mismatch');
if (n.expected_release_assets[0].name !== 'nft-0xabc-1.tar') throw new Error('asset name mismatch');
if (n.expected_release_assets[0].files[0].expected_sha256 !== 'a'.repeat(64)) throw new Error('sha256 mismatch');
if (n.does_not_prove.length < 1) throw new Error('does_not_prove empty');

console.log('VERIFY_RELEASE_ASSETS_CONSUMES_NFT_CARS_MANIFEST_OK');
"""

with tempfile.NamedTemporaryFile("w", suffix=".mjs", delete=False, dir=ROOT) as f:
    f.write(test_code)
    p = Path(f.name)

try:
    res = subprocess.run(["node", str(p)], cwd=ROOT, text=True, capture_output=True)
finally:
    p.unlink(missing_ok=True)

if res.returncode != 0:
    print(res.stdout)
    print(res.stderr)
    sys.exit(res.returncode)

print(res.stdout.strip())
