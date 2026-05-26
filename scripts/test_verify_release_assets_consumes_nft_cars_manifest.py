#!/usr/bin/env python3
"""Test: verify-release-assets.mjs can normalize real part-based manifest"""

import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

test_code = r"""
import { normalizeReleaseManifest } from './scripts/verify-release-assets.mjs';

// Test 1: Real part-based manifest (what download-nft-cars.mjs actually produces)
const m = {
  schema: 'trinity-release-manifest-v1',
  release_kind: 'nft-car-backup-parts',
  actual_nfts: 2,
  total_car_files: 4,
  contracts: 1,
  release_assets: [
    {
      asset_name: 'nft-cars-part01.tar.gz',
      files: [
        { role: 'metadata', contract: '0xabc', token_id: '1', txid: 'txMeta1', expected_path: 'txMeta1.car', expected_sha256: 'a'.repeat(64), expected_size: 100, expected_root_cid: 'bafyMeta1', cid_check_required: false },
        { role: 'media', contract: '0xabc', token_id: '1', txid: 'txMed1', expected_path: 'txMed1.car', expected_sha256: 'b'.repeat(64), expected_size: 200, expected_root_cid: 'bafyMed1', cid_check_required: false },
      ]
    },
    {
      asset_name: 'nft-cars-part02.tar.gz',
      files: [
        { role: 'metadata', contract: '0xabc', token_id: '2', txid: 'txMeta2', expected_path: 'txMeta2.car', expected_sha256: 'c'.repeat(64), expected_size: 150, expected_root_cid: 'bafyMeta2', cid_check_required: false },
        { role: 'media', contract: '0xabc', token_id: '2', txid: 'txMed2', expected_path: './txMed2.car', expected_sha256: 'd'.repeat(64), expected_size: 250, expected_root_cid: 'bafyMed2', cid_check_required: false },
      ]
    }
  ],
  auxiliary_assets: ['nft-cars-manifest.tar.gz', 'RELEASE-MANIFEST.json'],
  does_not_prove: ['CID/root/DAG correctness unless cid_check_enabled is true'],
};

const n = normalizeReleaseManifest(m);

if (n.schema !== 'trinity-release-manifest-v1') throw new Error('schema mismatch');
if (n.expected_release_assets.length !== 2) throw new Error('expected 2 assets, got ' + n.expected_release_assets.length);
if (n.expected_asset_count !== 2) throw new Error('expected_asset_count mismatch');
if (n.expected_car_count !== 4) throw new Error('expected_car_count mismatch: ' + n.expected_car_count);
if (n.expected_release_assets[0].name !== 'nft-cars-part01.tar.gz') throw new Error('asset name mismatch');
if (n.expected_release_assets[0].files[0].expected_sha256 !== 'a'.repeat(64)) throw new Error('sha256 mismatch');
if (n.expected_release_assets[1].files[1].expected_path !== 'txMed2.car') throw new Error('./ normalization failed');
if (n.auxiliary_assets.length !== 2) throw new Error('auxiliary_assets missing');

// Test 2: Reject release_assets as object (not array)
let threw = false;
try {
  normalizeReleaseManifest({
    schema: 'trinity-release-manifest-v1',
    release_assets: { parts: ['nft-cars-part01.tar.gz'] }
  });
} catch (e) { threw = true; }
if (!threw) throw new Error('Should reject release_assets as object');

// Test 3: Legacy per_nft_assets still works
const legacy = {
  schema: 'trinity-release-manifest-v1',
  actual_nfts: 1,
  total_car_files: 2,
  per_nft_assets: [{
    nft_asset_name: 'nft-0xabc-1.tar',
    files: [
      { role: 'metadata', expected_sha256: 'e'.repeat(64), expected_size: 50 },
    ]
  }],
};
const ln = normalizeReleaseManifest(legacy);
if (ln.expected_release_assets[0].name !== 'nft-0xabc-1.tar') throw new Error('legacy normalization failed');

console.log('VERIFY_RELEASE_ASSETS_CONSUMES_PART_MANIFEST_OK');
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
