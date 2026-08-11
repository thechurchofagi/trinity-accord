#!/usr/bin/env bash
set -euo pipefail

echo "== Trinity Accord V3/V4/V4+ GitHub/Release-First Signed Manifest Audit =="

command -v node >/dev/null 2>&1 || { echo "Node.js required" >&2; exit 1; }
command -v python3 >/dev/null 2>&1 || { echo "Python3 required" >&2; exit 1; }

node --version
python3 --version

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
echo "== Verify GitHub / Release authority mirror coverage =="
node scripts/pull-authority-arweave-mirrors.mjs

echo
echo "== Verify signed manifest coverage =="
node scripts/verify-signed-manifest-coverage.mjs --target-manifest audit/v3plus-targets.json

echo
echo "== Verify release-aware GitHub archive mirror =="
bash scripts/verify-github-archive.sh

echo
echo "== Optional V5-style Arweave cross-source check =="
if [ "${RUN_CROSS_SOURCE:-0}" = "1" ]; then
  node scripts/pull-authority-arweave-mirrors.mjs --cross-source
else
  echo "Skipping cross-source Arweave check. Set RUN_CROSS_SOURCE=1 to run it."
fi

echo
echo "== Optional: run legacy full evidence chain with an explicit compatible 175-tar source =="
if [ -n "${GITHUB_TOKEN:-}" ] && [ -n "${ETH_RPC_URL:-}" ] && [ -n "${FEC_RELEASE_TAG:-}" ]; then
  node scripts/verify-full-evidence-chain.mjs \
    --release-tag "$FEC_RELEASE_TAG" \
    --ots-release-tag ots-and-flaw-mirror-v1 \
    --concurrency "${DAG_VERIFY_CONCURRENCY:-8}"
else
  echo "Skipping legacy full evidence chain. GITHUB_TOKEN, ETH_RPC_URL, and FEC_RELEASE_TAG naming a verified 175-tar source are all required."
fi

echo
echo "== Generated audits =="
ls -1 *AUDIT*.json || true
echo "DONE"
