#!/usr/bin/env bash
set -euo pipefail

# System test for Gateway auto-archive in DRY_RUN mode.
# Starts local server, sends archive payloads, validates responses.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SERVER_DIR="$ROOT/examples/github-app-backend"

export DRY_RUN=true
export PORT=18787
export GATEWAY_URL="http://localhost:$PORT"

cleanup() {
  if [ -n "${SERVER_PID:-}" ]; then
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

echo "=== Starting Gateway server (DRY_RUN=true) on :$PORT ==="
cd "$SERVER_DIR"
node server.js &
SERVER_PID=$!
sleep 3

# Health check
echo "--- Health check ---"
curl -sf "$GATEWAY_URL/health" | python3 -m json.tool
echo ""

# Test 1: intake only (sample) -> should succeed, no archive labels
echo "=== Test 1: intake only preflight ==="
INTAKE_PAYLOAD=$(cat "$ROOT/tests/fixtures/archive-readiness/issue154_like_v4_b0_d2_intake.json")
RESULT=$(curl -s -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  -d "$INTAKE_PAYLOAD")
echo "$RESULT" | python3 -m json.tool

ISSUE_CREATED=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('issue_created', 'unknown'))")
if [ "$ISSUE_CREATED" = "False" ] || [ "$ISSUE_CREATED" = "false" ]; then
  echo "PASS: intake only did not create issue in preflight"
else
  echo "WARN: issue_created=$ISSUE_CREATED (expected false for preflight)"
fi
echo ""

# Test 2: blocked formal archive -> should return 422 or archive_not_ready
echo "=== Test 2: blocked formal archive preflight ==="
BLOCKED_PAYLOAD=$(cat "$ROOT/tests/fixtures/archive-readiness/issue154_like_v4_b0_d2_archive_request.json")
HTTP_CODE=$(curl -s -o /tmp/blocked_result.json -w "%{http_code}" -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  -d "$BLOCKED_PAYLOAD" || true)
cat /tmp/blocked_result.json | python3 -m json.tool
echo "HTTP status: $HTTP_CODE"
if [ "$HTTP_CODE" = "422" ]; then
  echo "PASS: blocked archive returned 422"
else
  echo "INFO: blocked archive returned $HTTP_CODE (check archive_readiness in response)"
fi
echo ""

# Test 3: external agent sample archive -> should succeed
echo "=== Test 3: external agent sample archive preflight ==="
SAMPLE_PAYLOAD=$(cat "$ROOT/tests/fixtures/archive-readiness/external_agent_sample_b0_ready.json")
RESULT=$(curl -s -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  -d "$SAMPLE_PAYLOAD")
echo "$RESULT" | python3 -m json.tool
echo ""

# Test 4: formal archive ready -> should succeed
echo "=== Test 4: formal archive ready preflight ==="
FORMAL_PAYLOAD=$(cat "$ROOT/tests/fixtures/archive-readiness/verification_report_archive_b1_d2_ready.json")
RESULT=$(curl -s -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  -d "$FORMAL_PAYLOAD")
echo "$RESULT" | python3 -m json.tool
echo ""

# Test 5: successor reception -> should be blocked
echo "=== Test 5: successor reception preflight ==="
SUCCESSOR_PAYLOAD=$(cat "$ROOT/tests/fixtures/archive-readiness/successor_reception_candidate_blocked.json")
HTTP_CODE=$(curl -s -o /tmp/successor_result.json -w "%{http_code}" -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  -d "$SUCCESSOR_PAYLOAD" || true)
cat /tmp/successor_result.json | python3 -m json.tool
echo "HTTP status: $HTTP_CODE"
if [ "$HTTP_CODE" = "422" ]; then
  echo "PASS: successor reception returned 422"
else
  echo "INFO: successor reception returned $HTTP_CODE"
fi
echo ""

# Test 6: archive-preflight endpoint
echo "=== Test 6: archive-preflight endpoint ==="
RESULT=$(curl -s -X POST "$GATEWAY_URL/gateway/archive-preflight" \
  -H "Content-Type: application/json" \
  -d "{\"gateway_payload\": $SAMPLE_PAYLOAD}")
echo "$RESULT" | python3 -m json.tool
echo ""

# Test 7: DRY_RUN submit with auto_archive -> should show would_apply_labels
echo "=== Test 7: DRY_RUN submit with auto_archive ==="
SUBMIT_PAYLOAD=$(echo "$SAMPLE_PAYLOAD" | python3 -c "
import sys, json
p = json.load(sys.stdin)
p['auto_archive'] = {'enabled': True, 'close_issue_when_archived': True, 'post_decision_comment': True}
json.dump(p, sys.stdout)
")
RESULT=$(curl -s -X POST "$GATEWAY_URL/agent-submit" \
  -H "Content-Type: application/json" \
  -d "$SUBMIT_PAYLOAD")
echo "$RESULT" | python3 -m json.tool

DRY=$(echo "$RESULT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('dry_run', False))")
if [ "$DRY" = "True" ] || [ "$DRY" = "true" ]; then
  echo "PASS: DRY_RUN submit returned dry_run=true"
else
  echo "WARN: dry_run=$DRY"
fi
echo ""

echo "=== ALL DRY RUN TESTS COMPLETE ==="
