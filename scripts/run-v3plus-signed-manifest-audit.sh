#!/usr/bin/env bash
set -euo pipefail

echo "== Trinity Accord V3/V4/V4+ GitHub-First Signed Manifest Audit =="

if ! command -v node >/dev/null 2>&1; then
  echo "Node.js is required." >&2
  exit 1
fi

if ! command -v python3 >/dev/null 2>&1; then
  echo "Python 3 is required." >&2
  exit 1
fi

node --version
python3 --version

echo
echo "== Install Node dependencies =="
if [ -f package.json ]; then
  npm install
fi

echo
echo "== Verify BTC BIP340 signature coverage =="
node scripts/verify-btc-signature-coverage.mjs

echo
echo "== Verify legacy ETH witness =="
node scripts/verify-legacy-eth-witness.mjs

echo
echo "== Verify GitHub-first authority mirror coverage =="
node scripts/pull-authority-arweave-mirrors.mjs

echo
echo "== Verify signed manifest coverage =="
if [ -f audit/v3plus-targets.json ]; then
  node scripts/verify-signed-manifest-coverage.mjs --target-manifest audit/v3plus-targets.json
else
  node scripts/verify-signed-manifest-coverage.mjs
fi

echo
echo "== Optional V5-style cross-source Arweave check =="
if [ "${RUN_CROSS_SOURCE:-0}" = "1" ]; then
  node scripts/pull-authority-arweave-mirrors.mjs --cross-source
else
  echo "Skipping cross-source Arweave check. Set RUN_CROSS_SOURCE=1 to run it."
fi

echo
echo "== Optional: run existing full evidence chain if ETH RPC and GitHub token are available =="
if [ -n "${GITHUB_TOKEN:-}" ] && [ -n "${ETH_RPC_URL:-}" ]; then
  node scripts/verify-full-evidence-chain.mjs \
    --release-tag nft-arweave-mirror-175-v1 \
    --ots-release-tag ots-and-flaw-mirror-v1 \
    --concurrency "${DAG_VERIFY_CONCURRENCY:-8}"
else
  echo "Skipping full evidence chain because GITHUB_TOKEN or ETH_RPC_URL is missing."
fi

echo
echo "== Generated audits =="
ls -1 *AUDIT*.json || true
echo "DONE"
