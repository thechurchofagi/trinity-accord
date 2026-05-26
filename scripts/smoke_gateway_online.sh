#!/usr/bin/env bash
set -euo pipefail

BASE="${GATEWAY_BASE_URL:-https://trinity-agent-issue-gateway.onrender.com}"

echo "Checking Gateway at ${BASE}"

# Try health endpoints first, then root
for endpoint in /healthz /readiness /; do
    if curl -fsS "${BASE}${endpoint}" >/dev/null 2>&1; then
        echo "PASS: Gateway reachable at ${endpoint}"
        echo "NOTE: This script does not submit an archive. Full E2E submission requires maintainer approval."
        exit 0
    fi
done

echo "FAIL: Gateway not reachable at any endpoint (${BASE})"
exit 1
