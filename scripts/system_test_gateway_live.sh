#!/usr/bin/env bash
# Smoke test for the live Gateway.
# Usage: GATEWAY_URL=https://trinity-agent-issue-gateway.onrender.com bash scripts/system_test_gateway_live.sh
set -euo pipefail

GATEWAY_URL="${GATEWAY_URL:?Set GATEWAY_URL}"
FAIL=0

echo "=== Gateway version ==="
curl -fsS "$GATEWAY_URL/gateway/version" | jq . || { echo "FAIL: version"; FAIL=1; }

echo ""
echo "=== Gateway capabilities ==="
curl -fsS "$GATEWAY_URL/gateway/capabilities" | jq . || { echo "FAIL: capabilities"; FAIL=1; }

echo ""
echo "=== Gateway examples ==="
curl -fsS "$GATEWAY_URL/gateway/examples/verification-report-candidate" | jq . || { echo "FAIL: report example"; FAIL=1; }
curl -fsS "$GATEWAY_URL/gateway/examples/verification-echo-candidate" | jq . || { echo "FAIL: echo example"; FAIL=1; }
curl -fsS "$GATEWAY_URL/gateway/examples/evidence-input-b1-external-explorer" | jq . || { echo "FAIL: b1 evidence example"; FAIL=1; }

echo ""
echo "=== Evidence input v4 alias (deprecated) ==="
V4_RESP=$(curl -s "$GATEWAY_URL/gateway/examples/evidence-input-v4-external-explorer")
V4_DEPRECATED=$(echo "$V4_RESP" | jq -r '.deprecated_alias // false')
if [ "$V4_DEPRECATED" != "true" ]; then
  echo "FAIL: v4 endpoint should return deprecated_alias=true"
  FAIL=1
fi

echo ""
echo "=== Lint evidence (valid) ==="
LINT_RESP=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/gateway/lint-evidence" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/evidence-input/valid_v4_external_explorer_example.json)
LINT_CODE=$(echo "$LINT_RESP" | tail -1)
LINT_BODY=$(echo "$LINT_RESP" | sed '$d')
echo "HTTP $LINT_CODE"
echo "$LINT_BODY" | jq .
if [ "$LINT_CODE" != "200" ]; then
  echo "FAIL: valid evidence lint should return 200"
  FAIL=1
fi

echo ""
echo "=== Preflight: valid payload ==="
VALID_RESP=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/gateway/valid_verification_report_candidate.json)
VALID_CODE=$(echo "$VALID_RESP" | tail -1)
VALID_BODY=$(echo "$VALID_RESP" | sed '$d')
echo "HTTP $VALID_CODE"
echo "$VALID_BODY" | jq .
if [ "$VALID_CODE" != "200" ]; then
  echo "FAIL: valid payload preflight should return 200"
  FAIL=1
fi
ACCEPTED=$(echo "$VALID_BODY" | jq -r '.accepted // false')
CREATED=$(echo "$VALID_BODY" | jq -r '.issue_created // "unknown"')
if [ "$ACCEPTED" != "true" ]; then
  echo "FAIL: valid payload should be accepted"
  FAIL=1
fi
if [ "$CREATED" != "false" ]; then
  echo "FAIL: preflight must not create issue (got issue_created=$CREATED)"
  FAIL=1
fi

echo ""
echo "=== Preflight: invalid payload ==="
INVALID_RESP=$(curl -s -w "\n%{http_code}" -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/gateway/invalid_issue_151_style_payload.json)
INVALID_CODE=$(echo "$INVALID_RESP" | tail -1)
INVALID_BODY=$(echo "$INVALID_RESP" | sed '$d')
echo "HTTP $INVALID_CODE"
echo "$INVALID_BODY" | jq .
if [ "$INVALID_CODE" != "422" ]; then
  echo "FAIL: invalid payload preflight should return 422"
  FAIL=1
fi

echo ""
if [ "$FAIL" -ne 0 ]; then
  echo "GATEWAY SMOKE TEST: SOME FAILURES"
  exit 1
fi
echo "GATEWAY SMOKE TEST: ALL PASS"
