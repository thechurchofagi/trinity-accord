#!/usr/bin/env bash
set -euo pipefail

BASE="${GATEWAY_BASE_URL:-https://trinity-agent-issue-gateway.onrender.com}"

echo "Checking Gateway at ${BASE}"
echo "NOTE: This smoke checks Gateway reachability only."
echo "NOTE: It does not validate live site discovery, Gateway preflight semantics, issue creation, archive automation, or Pages deployment."
echo "NOTE: Use scripts/smoke_live_discovery_contract.py for live public discovery freshness."

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
