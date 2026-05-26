#!/usr/bin/env bash
set -euo pipefail

BASE="${GATEWAY_BASE_URL:-https://trinity-agent-issue-gateway.onrender.com}"

echo "Checking Gateway health at ${BASE}"

curl -fsS "${BASE}/" >/dev/null || {
  echo "FAIL: Gateway root not reachable"
  exit 1
}

echo "Gateway root reachable."

# Intentionally do not submit a real archive here.
# A real end-to-end submission should use a dedicated fixture and maintainer approval.
echo "PASS: Gateway online smoke root check"
