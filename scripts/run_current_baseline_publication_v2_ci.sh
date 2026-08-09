#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

AUTH="preservation/current-baseline-publication-authorization-v2.json"
WORK_STATE="preservation/current-baseline-publish-v2-work.json"
PREPARE_MESSAGE="archive: prepare final proof baseline publication v2"
SEAL_MESSAGE="archive: record final proof baseline publication v2"
EXPECTED_RIGHTS_ACK="TRINITY_PRESERVATION_CAPSULE_RIGHTS_V1_APPROVED"

status="$(python3 - <<'PY'
import json
from pathlib import Path
print(json.loads(Path('preservation/current-baseline-publication-authorization-v2.json').read_text())['status'])
PY
)"

if [[ "$status" == "consumed" ]]; then
  python3 scripts/current_baseline_publication_v2.py validate
  echo "Final proof baseline publication v2 is consumed and publicly proven; no external write will run."
  exit 0
fi

if [[ "$status" != "pending" && "$status" != "prepared" ]]; then
  echo "::error::Unexpected final proof baseline v2 authorization status: $status"
  exit 1
fi

: "${RUNNER_TEMP:?RUNNER_TEMP is required}"
: "${ZENODO_ACCESS_TOKEN:?ZENODO_ACCESS_TOKEN is required}"
ZENODO_API_BASE="${ZENODO_API_BASE:-https://zenodo.org/api}"
committed_rights_ack="$(python3 - <<'PY'
import json
print(json.load(open('preservation/current-baseline-publication-authorization-v2.json'))['zenodo_rights_acknowledgement'])
PY
)"
if [[ "$committed_rights_ack" != "$EXPECTED_RIGHTS_ACK" ]]; then
  echo "::error::Committed sequence-2 repository preservation rights acknowledgement mismatch."
  exit 1
fi
if [[ -n "${PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK:-}" \
  && "$PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK" != "$committed_rights_ack" ]]; then
  echo "::error::Environment rights acknowledgement conflicts with committed sequence-2 authorization."
  exit 1
fi
export PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK="$committed_rights_ack"

python3 scripts/current_baseline_publication_v2.py validate

git config user.name "github-actions[bot]"
git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
git fetch origin main --prune
git checkout -B main origin/main

status="$(python3 - <<'PY'
import json
print(json.load(open('preservation/current-baseline-publication-authorization-v2.json'))['status'])
PY
)"

if [[ "$status" == "pending" ]]; then
  required="$(python3 - <<'PY'
import json
print(json.load(open('preservation/current-baseline-publication-authorization-v2.json'))['required_proof_hardening_commit_sha'])
PY
)"
  git cat-file -e "$required^{commit}"
  if ! git merge-base --is-ancestor "$required" HEAD; then
    echo "::error::Required proof-hardening commit is not an ancestor of the publication base."
    exit 1
  fi
  if ! git diff --quiet "$required"..HEAD -- \
    evidence/ethereum-evidence-annex-v1 \
    evidence/nft-proof-annex-v1 \
    evidence/ethereum-proof-primitives-v1 \
    tests/test_nft_proof_annex_fail_closed.py \
    tests/test_ethereum_proof_primitives_parity.py; then
    echo "::error::Proof-hardened bytes changed after the explicitly authorized hardening commit."
    git diff --stat "$required"..HEAD -- \
      evidence/ethereum-evidence-annex-v1 \
      evidence/nft-proof-annex-v1 \
      evidence/ethereum-proof-primitives-v1 \
      tests/test_nft_proof_annex_fail_closed.py \
      tests/test_ethereum_proof_primitives_parity.py
    exit 1
  fi

  base_commit="$(git rev-parse HEAD)"
  python3 scripts/current_baseline_publication_v2.py prepare --base-commit "$base_commit"
  git add \
    "$AUTH" \
    preservation/current-baseline-publication-prepared-v2.json \
    preservation/repository-preservation-state-v2.json \
    api/recovery-index.json
  git commit -m "$PREPARE_MESSAGE"

  pushed=false
  for attempt in 1 2 3; do
    if git push origin HEAD:main; then
      pushed=true
      break
    fi
    git fetch origin main --prune
    git rebase origin/main
    sleep $((attempt * 5))
  done
  if [[ "$pushed" != true ]]; then
    echo "::error::Could not push prepared sequence-2 publication state."
    exit 1
  fi
  source_sha="$(git rev-parse HEAD)"
elif [[ "$status" == "prepared" ]]; then
  source_sha="$(git log origin/main --format='%H' --fixed-strings --grep="$PREPARE_MESSAGE" -1)"
  if [[ -z "$source_sha" ]]; then
    echo "::error::Prepared sequence-2 publication has no immutable source-baseline commit."
    exit 1
  fi
  git checkout -B main origin/main
else
  echo "::error::Authorization changed to an unexpected state while acquiring main."
  exit 1
fi

prepared_status="$(git show "$source_sha:$AUTH" | python3 -c 'import json,sys; print(json.load(sys.stdin)["status"])')"
if [[ "$prepared_status" != "prepared" ]]; then
  echo "::error::Immutable sequence-2 source commit does not contain prepared authorization."
  exit 1
fi
required="$(git show "$source_sha:$AUTH" | python3 -c 'import json,sys; print(json.load(sys.stdin)["required_proof_hardening_commit_sha"])')"
if ! git merge-base --is-ancestor "$required" "$source_sha"; then
  echo "::error::Immutable sequence-2 source does not descend from required proof hardening."
  exit 1
fi
if ! git diff --quiet "$required".."$source_sha" -- \
  evidence/ethereum-evidence-annex-v1 \
  evidence/nft-proof-annex-v1 \
  evidence/ethereum-proof-primitives-v1 \
  tests/test_nft_proof_annex_fail_closed.py \
  tests/test_ethereum_proof_primitives_parity.py; then
  echo "::error::Immutable sequence-2 source changed authorized proof-hardened bytes."
  exit 1
fi

python3 scripts/current_baseline_publication_v2.py validate
python3 scripts/audit_recovery_readiness.py
python3 scripts/toolchain_provenance.py > "$RUNNER_TEMP/toolchain-provenance.json"
cat "$RUNNER_TEMP/toolchain-provenance.json"

capsule="$RUNNER_TEMP/repository-preservation-refresh"
local_restore="$RUNNER_TEMP/local-restored-repository"
public_restore="$RUNNER_TEMP/public-restored-repository"
rm -rf "$capsule" "$local_restore" "$public_restore"

python3 scripts/build_preservation_capsule.py \
  --repository-root . \
  --commit "$source_sha" \
  --output-dir "$capsule"

mkdir -p "$RUNNER_TEMP/local-bootstrap"
cp "$capsule/restore-trinity-accord.py" "$RUNNER_TEMP/local-bootstrap/restore-trinity-accord.py"
python3 "$RUNNER_TEMP/local-bootstrap/restore-trinity-accord.py" \
  --deposit-dir "$capsule" \
  --output-dir "$local_restore"

local_source="$(python3 - <<PY
import json
print(json.load(open('$local_restore/recovery-report.json'))['source_git_commit_sha'])
PY
)"
if [[ "$local_source" != "$source_sha" ]]; then
  echo "::error::Local sequence-2 GitHub-zero recovery source mismatch."
  exit 1
fi

# Fail closed before any external write if the authenticated preservation
# series has moved unexpectedly or contains an unrelated unfinished draft.
# A retry after an ambiguous prior attempt may continue only when the newest
# published/draft object has the exact capsule id being reconciled.
CAPSULE_DIR="$capsule" ZENODO_API_BASE="$ZENODO_API_BASE" python3 - <<'PY'
import os
import sys
from pathlib import Path
sys.path.insert(0, str(Path('scripts').resolve()))
import publish_preservation_capsule_to_zenodo as pub

previous_doi = '10.5281/zenodo.21831412'
concept_doi = '10.5281/zenodo.21739343'
concept_record_id = 21739343
package = pub.verify_local_package(Path(os.environ['CAPSULE_DIR']))
client = pub.ZenodoClient(os.environ['ZENODO_ACCESS_TOKEN'].strip(), os.environ['ZENODO_API_BASE'])
series = pub.series_records(pub.list_depositions(client))
for item in series:
    pub.require_concept_series(item, concept_doi, concept_record_id)
published = [item for item in series if pub.is_published(item)]
drafts = [item for item in series if not pub.is_published(item)]
if not published:
    raise SystemExit('Zenodo preservation series has no published predecessor')
latest = published[-1]
matching_published = [item for item in published if pub.capsule_id(item) == package['capsule_id']]
matching_drafts = [item for item in drafts if pub.capsule_id(item) == package['capsule_id']]
unrelated_drafts = [item for item in drafts if pub.capsule_id(item) != package['capsule_id']]
if unrelated_drafts:
    raise SystemExit('unrelated unfinished Zenodo preservation draft exists; refusing sequence-2 publication')
if matching_published:
    if len(matching_published) != 1 or pub.deposition_id(matching_published[0]) != pub.deposition_id(latest):
        raise SystemExit('matching sequence-2 publication exists but is not the latest preservation version')
    print(f"Reconciling already-published exact capsule: {pub.doi(matching_published[0])}")
elif pub.doi(latest) != previous_doi:
    raise SystemExit(f"Zenodo preservation lineage moved unexpectedly: latest={pub.doi(latest)!r} expected={previous_doi!r}")
elif len(matching_drafts) > 1:
    raise SystemExit('multiple matching sequence-2 drafts exist')
else:
    print(f"Zenodo lineage preflight PASS: previous={previous_doi} capsule={package['capsule_id']}")
PY

cp preservation/repository-preservation-state-v2.json "$WORK_STATE"
python3 scripts/publish_preservation_capsule_to_zenodo_v3.py \
  --capsule-dir "$capsule" \
  --state "$WORK_STATE" \
  --api-base "$ZENODO_API_BASE" \
  --rights-boundary-ack "$PRESERVATION_CAPSULE_ZENODO_RIGHTS_ACK"

record_id="$(python3 - <<'PY'
import json
print(json.load(open('preservation/current-baseline-publish-v2-work.json'))['latest_record_id'])
PY
)"
if [[ ! "$record_id" =~ ^[0-9]+$ ]]; then
  echo "::error::Sequence-2 publisher did not record a valid Zenodo record id."
  exit 1
fi

mkdir -p "$RUNNER_TEMP/public-bootstrap"
cp "$capsule/restore-trinity-accord.py" "$RUNNER_TEMP/public-bootstrap/restore-trinity-accord.py"
python3 "$RUNNER_TEMP/public-bootstrap/restore-trinity-accord.py" \
  --zenodo-record-id "$record_id" \
  --output-dir "$public_restore"

public_source="$(python3 - <<PY
import json
print(json.load(open('$public_restore/recovery-report.json'))['source_git_commit_sha'])
PY
)"
if [[ "$public_source" != "$source_sha" ]]; then
  echo "::error::Public sequence-2 DOI-only recovery source mismatch."
  exit 1
fi

python3 scripts/current_baseline_publication_v2.py seal \
  --source-commit "$source_sha" \
  --published-state "$WORK_STATE" \
  --recovery-report "$public_restore/recovery-report.json"
python3 scripts/current_baseline_publication_v2.py validate

git add \
  "$AUTH" \
  preservation/current-baseline-publication-prepared-v2.json \
  preservation/current-baseline-publication-observation-v2.json \
  preservation/repository-preservation-state-v2.json \
  api/recovery-index.json

if git diff --cached --quiet; then
  echo "Final proof baseline v2 state is already recorded."
  exit 0
fi

git commit -m "$SEAL_MESSAGE"
for attempt in 1 2 3; do
  if git push origin HEAD:main; then
    exit 0
  fi
  git fetch origin main --prune
  git rebase origin/main
  sleep $((attempt * 5))
done

echo "::error::Zenodo sequence-2 publication succeeded but verified final state could not be pushed. Rerun will reconcile the exact capsule instead of creating another version."
exit 1
