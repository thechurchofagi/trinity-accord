#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${ZENODO_ACCESS_TOKEN:?ZENODO_ACCESS_TOKEN is required}"
: "${PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK:?PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK is required}"

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git fetch origin main --prune
git checkout -B main origin/main

python3 scripts/migrate_repository_preservation_semantics_v3.py

git add \
  RECOVERY.md \
  api/recovery-index.json \
  preservation/recovery-catalog.json \
  preservation/repository-preservation-refresh-authorization.json \
  preservation/repository-preservation-state-v2.json \
  scripts/build_preservation_capsule.py \
  scripts/preservation_capsule.py \
  scripts/repository_preservation_refresh.py \
  scripts/restore_preservation_capsule.py \
  tests/test_preservation_capsule.py \
  tests/test_repository_preservation_refresh_contract.py

if [[ -e preservation/repository-preservation-refresh-prepared.json ]]; then
  git add preservation/repository-preservation-refresh-prepared.json
else
  git rm --cached --ignore-unmatch \
    preservation/repository-preservation-refresh-prepared.json >/dev/null 2>&1 || true
fi

if ! git diff --cached --quiet; then
  git commit -m "fix: finalize repository publication-baseline semantics"
  git push origin HEAD:main
fi

exec bash scripts/run_repository_preservation_refresh_ci.sh
