#!/usr/bin/env bash
# verify-github-archive.sh — Verify the GitHub archive mirror against hash-manifest.json
# Usage: bash scripts/verify-github-archive.sh
#
# This script verifies that all files in archive/ match their expected SHA-256 hashes
# as recorded in archive/hash-manifest.json. It does NOT fetch from Arweave or ETH.
#
# Boundary: non-amending; BTC originals prevail.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
MANIFEST="$REPO_DIR/archive/hash-manifest.json"

if [ ! -f "$MANIFEST" ]; then
  echo "❌ hash-manifest.json not found at $MANIFEST"
  echo "   Run the archive workflow first."
  exit 1
fi

echo "=== Trinity Accord — GitHub Archive Verification ==="
echo "Manifest: $MANIFEST"
echo "Date: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

PASS=0
FAIL=0
MISSING=0
TOTAL=0

# Parse manifest and verify each file
python3 -c "
import json, hashlib, sys, os

repo = '$REPO_DIR'
with open('$MANIFEST') as f:
    manifest = json.load(f)

pass_c = fail_c = missing_c = 0
total = len(manifest['files'])

for entry in manifest['files']:
    path = os.path.join(repo, entry['path'])
    expected = entry.get('sha256', '')
    if not expected:
        continue

    if not os.path.exists(path):
        print(f'  ❌ MISSING  {entry[\"path\"]}')
        missing_c += 1
        continue

    with open(path, 'rb') as f:
        actual = hashlib.sha256(f.read()).hexdigest()

    if actual == expected:
        print(f'  ✅ PASS     {entry[\"path\"]}')
        pass_c += 1
    else:
        print(f'  ❌ FAIL     {entry[\"path\"]}')
        print(f'             expected: {expected}')
        print(f'             actual:   {actual}')
        fail_c += 1

print()
print(f'=== RESULTS ===')
print(f'Files checked: {total}')
print(f'PASS: {pass_c}  FAIL: {fail_c}  MISSING: {missing_c}')

if fail_c > 0 or missing_c > 0:
    print()
    print('⚠️  Some files failed verification.')
    print('   If Arweave originals are available, re-download the failed files.')
    sys.exit(1)
else:
    print()
    print('✅ All files verified. GitHub mirror matches expected hashes.')
    sys.exit(0)
"
