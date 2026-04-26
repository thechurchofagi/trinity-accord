#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <worker-base-url>"
  echo "Example: $0 https://echo-submission-proxy.<subdomain>.workers.dev"
  exit 1
fi

BASE_URL="${1%/}"

check() {
  local path="$1"
  local expected_code="$2"
  echo "\n=== ${path} ==="
  local headers body status
  headers=$(mktemp)
  body=$(mktemp)
  status=$(curl -sS -D "$headers" -o "$body" -w "%{http_code}" "${BASE_URL}${path}")
  echo "Status: ${status}"
  echo "Version header: $(grep -i '^x-echo-worker-version:' "$headers" | tr -d '\r' || true)"
  echo "Body preview:"
  head -c 240 "$body"; echo

  if [[ "$status" != "$expected_code" ]]; then
    echo "[FAIL] Expected HTTP ${expected_code}, got ${status}"
    exit 2
  fi
}

check "/health" "200"
check "/version" "200"
check "/submit-echo" "200"

echo "\nAll checks passed."
