#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

: "${RUNNER_TEMP:?RUNNER_TEMP is required}"
: "${ZENODO_ACCESS_TOKEN:?ZENODO_ACCESS_TOKEN is required}"
: "${PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK:?PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK is required}"
ZENODO_API_BASE="${ZENODO_API_BASE:-https://zenodo.org/api}"

if [[ "$PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK" != \
  "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED" ]]; then
  echo "::error::Repository preservation rights acknowledgement mismatch."
  exit 1
fi

python3 scripts/repository_preservation_refresh.py validate

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git fetch origin main --prune
git checkout -B main origin/main

status="$(python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('preservation/repository-preservation-refresh-authorization.json').read_text())['status'])
PY
)"

if [[ "$status" == "consumed" ]]; then
  echo "Repository preservation refresh is already consumed and publicly proven."
  exit 0
fi

if [[ "$status" == "pending" ]]; then
  base_commit="$(git rev-parse HEAD)"
  python3 scripts/repository_preservation_refresh.py prepare \
    --base-commit "$base_commit"
  git add \
    RECOVERY.md \
    api/recovery-index.json \
    preservation/EXTERNAL-BINARY-ANNEX.md \
    preservation/repository-preservation-refresh-authorization.json \
    preservation/repository-preservation-refresh-prepared.json \
    preservation/repository-preservation-state-v2.json
  git commit -m "archive: prepare repository preservation refresh v2"
  git push origin HEAD:main
  source_sha="$(git rev-parse HEAD)"
elif [[ "$status" == "prepared" ]]; then
  source_sha="$(git log origin/main --format='%H' --fixed-strings \
    --grep='archive: prepare repository preservation refresh v2' -1)"
  if [[ -z "$source_sha" ]]; then
    echo "::error::Prepared refresh has no immutable source-baseline commit."
    exit 1
  fi
  git checkout -B main origin/main
else
  echo "::error::Unexpected repository refresh authorization status: $status"
  exit 1
fi

git cat-file -e "$source_sha^{commit}"
prepared_status="$(git show \
  "$source_sha:preservation/repository-preservation-refresh-authorization.json" | \
  python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])')"
if [[ "$prepared_status" != "prepared" ]]; then
  echo "::error::Immutable source commit does not contain prepared authorization."
  exit 1
fi

python3 scripts/repository_preservation_refresh.py validate
python3 scripts/audit_recovery_readiness.py
python3 scripts/toolchain_provenance.py > "$RUNNER_TEMP/toolchain-provenance.json"
cat "$RUNNER_TEMP/toolchain-provenance.json"

capsule="$RUNNER_TEMP/repository-preservation-refresh"
local_restore="$RUNNER_TEMP/local-restored-repository"
public_restore="$RUNNER_TEMP/public-restored-repository"
metadata_report="$RUNNER_TEMP/public-metadata-report.json"
rm -rf "$capsule" "$local_restore" "$public_restore" "$metadata_report"

python3 scripts/build_preservation_capsule.py \
  --repository-root . \
  --commit "$source_sha" \
  --output-dir "$capsule"

mkdir -p "$RUNNER_TEMP/local-bootstrap"
cp "$capsule/restore-trinity-accord.py" \
  "$RUNNER_TEMP/local-bootstrap/restore-trinity-accord.py"
python3 "$RUNNER_TEMP/local-bootstrap/restore-trinity-accord.py" \
  --deposit-dir "$capsule" \
  --output-dir "$local_restore"

local_source="$(python3 - <<PY
import json
print(json.load(open('$local_restore/recovery-report.json'))['source_git_commit_sha'])
PY
)"
if [[ "$local_source" != "$source_sha" ]]; then
  echo "::error::Local GitHub-zero recovery source mismatch."
  exit 1
fi

python3 scripts/publish_preservation_capsule_to_zenodo.py \
  --capsule-dir "$capsule" \
  --state preservation/repository-preservation-state-v2.json \
  --api-base "$ZENODO_API_BASE" \
  --rights-boundary-ack "$PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK"

record_id="$(python3 - <<'PY'
import json
from pathlib import Path
state = json.loads(Path('preservation/repository-preservation-state-v2.json').read_text())
print(state['latest_record_id'])
PY
)"
if [[ ! "$record_id" =~ ^[0-9]+$ ]]; then
  echo "::error::Publisher did not record a valid Zenodo record id."
  exit 1
fi

mkdir -p "$RUNNER_TEMP/public-bootstrap"
cp "$capsule/restore-trinity-accord.py" \
  "$RUNNER_TEMP/public-bootstrap/restore-trinity-accord.py"
python3 "$RUNNER_TEMP/public-bootstrap/restore-trinity-accord.py" \
  --zenodo-record-id "$record_id" \
  --output-dir "$public_restore"

public_source="$(python3 - <<PY
import json
print(json.load(open('$public_restore/recovery-report.json'))['source_git_commit_sha'])
PY
)"
if [[ "$public_source" != "$source_sha" ]]; then
  echo "::error::Public DOI-only recovery source mismatch."
  exit 1
fi

python3 scripts/repository_preservation_refresh.py verify-public \
  --record-id "$record_id" \
  --capsule-dir "$capsule" \
  --output "$metadata_report"

python3 scripts/repository_preservation_refresh.py seal \
  --source-commit "$source_sha" \
  --recovery-report "$public_restore/recovery-report.json" \
  --metadata-report "$metadata_report"

python3 scripts/repository_preservation_refresh.py validate

git add \
  api/recovery-index.json \
  preservation/repository-preservation-refresh-authorization.json \
  preservation/repository-preservation-refresh-prepared.json \
  preservation/repository-preservation-state-v2.json \
  preservation/repository-preservation-observation.json

if git diff --cached --quiet; then
  echo "Final repository preservation state is already recorded."
  exit 0
fi

git commit -m "archive: record refreshed repository preservation DOI"
for attempt in 1 2 3; do
  if git push origin HEAD:main; then
    exit 0
  fi
  git fetch origin main --prune
  git rebase origin/main
  git add \
    api/recovery-index.json \
    preservation/repository-preservation-refresh-authorization.json \
    preservation/repository-preservation-refresh-prepared.json \
    preservation/repository-preservation-state-v2.json \
    preservation/repository-preservation-observation.json
  if ! git diff --cached --quiet; then
    git commit --amend --no-edit
  fi
  sleep $((attempt * 5))
done

echo "::error::Zenodo publication succeeded but verified final state could not be pushed."
exit 1
