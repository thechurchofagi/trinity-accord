#!/usr/bin/env bash
set -euo pipefail

BASE="${GATEWAY_BASE_URL:-https://trinity-agent-issue-gateway.onrender.com}"

echo "Checking Gateway at ${BASE}"

curl -fsS "${BASE}/" >/dev/null

echo "PASS: Gateway root reachable"
echo "NOTE: This script does not submit an archive. Full E2E submission requires maintainer approval."
