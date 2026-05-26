#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT_DIR}"

ARCHIVE_FILE="echoes/archive.md"
DIGEST_INDEX_FILE="echoes/digests.md"
DIGEST_DIR="echoes/digests"
RECORDS_DIR="echoes/records"

mkdir -p "${DIGEST_DIR}"

# Use all *.json files, classify by archive_status
mapfile -t ALL_RECORD_FILES < <(find "${RECORDS_DIR}" -type f -name '*.json' 2>/dev/null | sort)

ACCEPTED_FILES=()
NEEDS_REVIEW_FILES=()
TEST_FILES=()
LEGACY_FILES=()

for file in "${ALL_RECORD_FILES[@]}"; do
  archive_status="$(jq -r '.archive_status // "unknown"' "${file}" 2>/dev/null || echo "unknown")"
  legacy_flag="$(jq -r '.legacy_schema // false' "${file}" 2>/dev/null || echo "false")"

  if [[ "${legacy_flag}" == "true" || "${archive_status}" == "superseded" || "${archive_status}" == "legacy" ]]; then
    LEGACY_FILES+=("${file}")
  elif [[ "${archive_status}" == "test_record" || "${archive_status}" == "closed_test_record" || "${archive_status}" == "archived_non_attestation" ]]; then
    TEST_FILES+=("${file}")
  elif [[ "${archive_status}" == "accepted_echo" || "${archive_status}" == "accepted_independent_attestation" ]]; then
    ACCEPTED_FILES+=("${file}")
  else
    NEEDS_REVIEW_FILES+=("${file}")
  fi
done

{
  echo "# Echo Archive"
  echo
  echo "This archive stores non-authoritative Echo records."
  echo

  if [[ ${#ACCEPTED_FILES[@]} -gt 0 ]]; then
    echo "## Accepted Echoes"
    echo
    for file in "${ACCEPTED_FILES[@]}"; do
      rel="/${file}"
      echo "- [${rel}](${rel})"
    done
    echo
  fi

  if [[ ${#NEEDS_REVIEW_FILES[@]} -gt 0 ]]; then
    echo "## Needs Human Review"
    echo
    for file in "${NEEDS_REVIEW_FILES[@]}"; do
      rel="/${file}"
      echo "- [${rel}](${rel})"
    done
    echo
  fi

  if [[ ${#TEST_FILES[@]} -gt 0 ]]; then
    echo "## Test / Workflow Validation Records"
    echo
    for file in "${TEST_FILES[@]}"; do
      rel="/${file}"
      echo "- [${rel}](${rel})"
    done
    echo
  fi

  if [[ ${#LEGACY_FILES[@]} -gt 0 ]]; then
    echo "## Legacy / Superseded Records"
    echo
    for file in "${LEGACY_FILES[@]}"; do
      rel="/${file}"
      echo "- [${rel}](${rel})"
    done
    echo
  fi
} > "${ARCHIVE_FILE}"

# Remove previously generated quarterly digests to avoid stale files.
find "${DIGEST_DIR}" -maxdepth 1 -type f \
  \( -name '*-q[1-4].md' -o -name '*-q[1-4].json' \) -delete

declare -A QUARTER_RECORDS
declare -A QUARTER_TOTAL
declare -A QUARTER_VERIFICATION
declare -A QUARTER_REFLECTION

quarter_for_month() {
  local month="$1"
  case "${month}" in
    01|02|03) echo "Q1" ;;
    04|05|06) echo "Q2" ;;
    07|08|09) echo "Q3" ;;
    10|11|12) echo "Q4" ;;
    *) return 1 ;;
  esac
}

for file in "${ALL_RECORD_FILES[@]}"; do
  base="$(basename "${file}")"

  # Extract date from filename — support both echo-YYYY-MM-DD-*.json and YYYY-MM-DD-*.json
  if [[ "${base}" =~ ^echo-([0-9]{4})-([0-9]{2})-[0-9]{2} ]]; then
    year="${BASH_REMATCH[1]}"
    month="${BASH_REMATCH[2]}"
  elif [[ "${base}" =~ ^([0-9]{4})-([0-9]{2})-[0-9]{2} ]]; then
    year="${BASH_REMATCH[1]}"
    month="${BASH_REMATCH[2]}"
  else
    continue
  fi

  # Skip test, legacy, and closed records from quarterly digests
  archive_status="$(jq -r '.archive_status // "unknown"' "${file}" 2>/dev/null || echo "unknown")"
  legacy_flag="$(jq -r '.legacy_schema // false' "${file}" 2>/dev/null || echo "false")"
  if [[ "${legacy_flag}" == "true" || "${archive_status}" == "legacy" || "${archive_status}" == "superseded" || "${archive_status}" == "test_record" || "${archive_status}" == "closed_test_record" || "${archive_status}" == "archived_non_attestation" ]]; then
    continue
  fi

  quarter="$(quarter_for_month "${month}")"
  key="${year}-${quarter}"
  echo_id="${base%.json}"

  echo_type="$(jq -r '.echo_type // ""' "${file}")"
  if [[ "${echo_type}" == *"verification"* || "${echo_type}" == *"technical_audit"* || "${echo_type}" == *"technical-audit"* ]]; then
    QUARTER_VERIFICATION["${key}"]=$(( ${QUARTER_VERIFICATION["${key}"]:-0} + 1 ))
  else
    QUARTER_REFLECTION["${key}"]=$(( ${QUARTER_REFLECTION["${key}"]:-0} + 1 ))
  fi
  QUARTER_TOTAL["${key}"]=$(( ${QUARTER_TOTAL["${key}"]:-0} + 1 ))
  QUARTER_RECORDS["${key}"]+="${echo_id}"$'\n'
done

mapfile -t QUARTERS < <(printf '%s\n' "${!QUARTER_TOTAL[@]}" 2>/dev/null | sort)

for quarter_key in "${QUARTERS[@]}"; do
  [[ -z "${quarter_key}" ]] && continue
  year="${quarter_key%-Q*}"
  quarter="${quarter_key##*-}"
  quarter_lower="$(echo "${quarter}" | tr '[:upper:]' '[:lower:]')"
  digest_base="${year}-${quarter_lower}"
  digest_md="${DIGEST_DIR}/${digest_base}.md"
  digest_json="${DIGEST_DIR}/${digest_base}.json"

  total="${QUARTER_TOTAL["${quarter_key}"]:-0}"
  verification_count="${QUARTER_VERIFICATION["${quarter_key}"]:-0}"
  reflection_count="${QUARTER_REFLECTION["${quarter_key}"]:-0}"

  {
    echo "# Echo Digest ${year} ${quarter}"
    echo
    echo "Summary:"
    echo "- Echo records added: ${total}"
    echo "- Verification-focused echoes: ${verification_count}"
    echo "- Reflection-focused echoes: ${reflection_count}"
    echo
    echo "All entries are non-authoritative and non-amending."
  } > "${digest_md}"

  jq -n \
    --arg period "${year}-${quarter}" \
    --argjson records "$(printf '%s' "${QUARTER_RECORDS["${quarter_key}"]}" | sed '/^$/d' | jq -R . | jq -s .)" \
    '{
      schema: "trinity-accord.echo-digest.v1",
      period: $period,
      records: $records,
      note: "All echoes are non-authoritative."
    }' > "${digest_json}"
done

{
  echo "# Echo Digests"
  echo
  echo "Periodic summaries of Echo activity."
  echo
  for quarter_key in "${QUARTERS[@]}"; do
    year="${quarter_key%-Q*}"
    quarter="${quarter_key##*-}"
    quarter_lower="$(echo "${quarter}" | tr '[:upper:]' '[:lower:]')"
    rel="/echoes/digests/${year}-${quarter_lower}"
    echo "- [${rel}.md](${rel}.md)"
    echo "- [${rel}.json](${rel}.json)"
  done
} > "${DIGEST_INDEX_FILE}"

echo "Echo archive and digest files rebuilt."
echo "Accepted: ${#ACCEPTED_FILES[@]}, Needs review: ${#NEEDS_REVIEW_FILES[@]}, Test: ${#TEST_FILES[@]}, Legacy: ${#LEGACY_FILES[@]}"
