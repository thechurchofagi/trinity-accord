#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON_BIN="${PYTHON:-python3}"
if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "::error::Configured Python interpreter is unavailable: $PYTHON_BIN"
  exit 1
fi

v3_authorization="preservation/current-baseline-publication-authorization-v3.json"
if [[ -f "$v3_authorization" ]]; then
  v3_status="$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('preservation/current-baseline-publication-authorization-v3.json').read_text())['status'])
PY
)"
  if [[ "$v3_status" == "consumed" ]]; then
    "$PYTHON_BIN" scripts/current_baseline_publication_v3.py validate
    echo "Final evidence baseline publication v3 is consumed and valid; no external write will run."
    exit 0
  fi
  if [[ "$v3_status" == "pending" || "$v3_status" == "prepared" ]]; then
    "$PYTHON_BIN" scripts/current_baseline_publication_v3.py validate
    if [[ "${GITHUB_EVENT_NAME:-}" == "push" \
      && "${GITHUB_REF:-}" == "refs/heads/main" \
      && "${TRINITY_PRESERVATION_REFRESH_EXECUTOR:-}" == "1" ]]; then
      bash scripts/run_current_baseline_publication_v3_ci.sh
      exit $?
    fi
    echo "Final evidence baseline publication v3 $v3_status state is valid; external publication requires the dedicated main-branch preservation executor."
    exit 0
  fi
  echo "::error::Unexpected current-baseline publication v3 status: $v3_status"
  exit 1
fi

v2_authorization="preservation/current-baseline-publication-authorization-v2.json"
if [[ -f "$v2_authorization" ]]; then
  v2_status="$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('preservation/current-baseline-publication-authorization-v2.json').read_text())['status'])
PY
)"
  if [[ "$v2_status" == "consumed" ]]; then
    "$PYTHON_BIN" scripts/current_baseline_publication_v2.py validate
    echo "Final proof baseline publication v2 is consumed and valid; no external write will run."
    exit 0
  fi
  if [[ "$v2_status" == "pending" || "$v2_status" == "prepared" ]]; then
    "$PYTHON_BIN" scripts/current_baseline_publication_v2.py validate
    if [[ "${GITHUB_EVENT_NAME:-}" == "push" \
      && "${GITHUB_REF:-}" == "refs/heads/main" \
      && "${TRINITY_PRESERVATION_REFRESH_EXECUTOR:-}" == "1" ]]; then
      bash scripts/run_current_baseline_publication_v2_ci.sh
      exit $?
    fi
    echo "Final proof baseline publication v2 $v2_status state is valid; external publication requires the dedicated main-branch preservation executor."
  else
    echo "::error::Unexpected current-baseline publication v2 status: $v2_status"
    exit 1
  fi
fi

current_status="$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
path = Path('preservation/current-baseline-publication-authorization-v1.json')
print(json.loads(path.read_text())['status'] if path.is_file() else 'absent')
PY
)"

# A newer, explicitly authorized repository-baseline lifecycle supersedes the
# older refresh transaction while it is prepared or after it is consumed. The
# last verified DOI remains the active published state throughout preparation.
if [[ "$current_status" == "prepared" ]]; then
  "$PYTHON_BIN" scripts/validate_current_baseline_prepared_state.py
  echo "Superseding current-baseline publication is prepared and valid; legacy refresh remains consumed."
  exit 0
fi
if [[ "$current_status" == "consumed" ]]; then
  "$PYTHON_BIN" scripts/validate_current_baseline_publication_state.py
  echo "Superseding current-baseline publication is consumed and valid; legacy refresh remains consumed."
  exit 0
fi

status="$("$PYTHON_BIN" - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('preservation/repository-preservation-refresh-authorization.json').read_text())['status'])
PY
)"

# A consumed authorization is an immutable, already-published terminal state.
# Reading that state is deliberately secret-independent: routine integrity runs
# must not fail merely because publication credentials or a repository variable
# are absent after the irreversible publication has already been completed.
# The committed authorization, DOI state, recovery proof, and observation still
# have to validate before the terminal no-op is accepted.
if [[ "$status" == "consumed" ]]; then
  "$PYTHON_BIN" scripts/repository_preservation_refresh.py validate
  echo "Repository preservation refresh is already consumed and publicly proven."
  exit 0
fi

: "${RUNNER_TEMP:?RUNNER_TEMP is required}"
: "${ZENODO_ACCESS_TOKEN:?ZENODO_ACCESS_TOKEN is required}"
: "${PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK:?PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK is required}"
ZENODO_API_BASE="${ZENODO_API_BASE:-https://zenodo.org/api}"

if [[ "$PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK" != \
  "TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED" ]]; then
  echo "::error::Repository preservation rights acknowledgement mismatch."
  exit 1
fi

"$PYTHON_BIN" scripts/repository_preservation_refresh.py validate

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git fetch origin main --prune
git checkout -B main origin/main

if [[ "$status" == "pending" ]]; then
  base_commit="$(git rev-parse HEAD)"
  "$PYTHON_BIN" scripts/migrate_repository_preservation_baseline_contract.py
  "$PYTHON_BIN" scripts/repository_preservation_refresh.py prepare \
    --base-commit "$base_commit"
  git add \
    RECOVERY.md \
    api/recovery-index.json \
    preservation/EXTERNAL-BINARY-ANNEX.md \
    preservation/repository-preservation-refresh-authorization.json \
    preservation/repository-preservation-refresh-prepared.json \
    preservation/repository-preservation-state-v2.json \
    tests/test_preservation_capsule.py
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
  "$PYTHON_BIN" -c 'import json,sys; print(json.load(sys.stdin)["status"])')"
if [[ "$prepared_status" != "prepared" ]]; then
  echo "::error::Immutable source commit does not contain prepared authorization."
  exit 1
fi

"$PYTHON_BIN" scripts/repository_preservation_refresh.py validate
"$PYTHON_BIN" scripts/audit_recovery_readiness.py
"$PYTHON_BIN" scripts/toolchain_provenance.py > "$RUNNER_TEMP/toolchain-provenance.json"
cat "$RUNNER_TEMP/toolchain-provenance.json"

capsule="$RUNNER_TEMP/repository-preservation-refresh"
local_restore="$RUNNER_TEMP/local-restored-repository"
public_restore="$RUNNER_TEMP/public-restored-repository"
metadata_report="$RUNNER_TEMP/public-metadata-report.json"
rm -rf "$capsule" "$local_restore" "$public_restore" "$metadata_report"

"$PYTHON_BIN" scripts/build_preservation_capsule.py \
  --repository-root . \
  --commit "$source_sha" \
  --output-dir "$capsule"

mkdir -p "$RUNNER_TEMP/local-bootstrap"
cp "$capsule/restore-trinity-accord.py" \
  "$RUNNER_TEMP/local-bootstrap/restore-trinity-accord.py"
"$PYTHON_BIN" "$RUNNER_TEMP/local-bootstrap/restore-trinity-accord.py" \
  --deposit-dir "$capsule" \
  --output-dir "$local_restore"

local_source="$("$PYTHON_BIN" - <<PY
import json
print(json.load(open('$local_restore/recovery-report.json'))['source_git_commit_sha'])
PY
)"
if [[ "$local_source" != "$source_sha" ]]; then
  echo "::error::Local GitHub-zero recovery source mismatch."
  exit 1
fi

# Zenodo draft objects can expose public download links that legitimately return
# 404 before publication. The V3 compatibility publisher reads unpublished
# bytes back from the authenticated upload bucket, verifies exact SHA-256, and
# still requires converged public metadata and public DOI-only recovery after
# publication. It reuses any matching prepared draft on retry.
"$PYTHON_BIN" scripts/publish_preservation_capsule_to_zenodo_v3.py \
  --capsule-dir "$capsule" \
  --state preservation/repository-preservation-state-v2.json \
  --api-base "$ZENODO_API_BASE" \
  --rights-boundary-ack "$PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK"

record_id="$("$PYTHON_BIN" - <<'PY'
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
"$PYTHON_BIN" "$RUNNER_TEMP/public-bootstrap/restore-trinity-accord.py" \
  --zenodo-record-id "$record_id" \
  --output-dir "$public_restore"

public_source="$("$PYTHON_BIN" - <<PY
import json
print(json.load(open('$public_restore/recovery-report.json'))['source_git_commit_sha'])
PY
)"
if [[ "$public_source" != "$source_sha" ]]; then
  echo "::error::Public DOI-only recovery source mismatch."
  exit 1
fi

"$PYTHON_BIN" scripts/repository_preservation_refresh.py verify-public \
  --record-id "$record_id" \
  --capsule-dir "$capsule" \
  --output "$metadata_report"

"$PYTHON_BIN" scripts/repository_preservation_refresh.py seal \
  --source-commit "$source_sha" \
  --recovery-report "$public_restore/recovery-report.json" \
  --metadata-report "$metadata_report"

"$PYTHON_BIN" scripts/repository_preservation_refresh.py validate

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
