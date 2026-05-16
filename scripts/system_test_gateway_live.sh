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
LINT_RESP=$(curl -s -X POST "$GATEWAY_URL/gateway/lint-evidence" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/evidence-input/valid_v4_external_explorer_example.json)
echo "$LINT_RESP" | jq .
LINT_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL/gateway/lint-evidence" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/evidence-input/valid_v4_external_explorer_example.json)
echo "HTTP $LINT_CODE"
if [ "$LINT_CODE" != "200" ]; then
  echo "FAIL: valid evidence lint should return 200"
  FAIL=1
fi

echo ""
echo "=== Build from evidence ==="
BUILD_RESP=$(curl -s -X POST "$GATEWAY_URL/gateway/build-from-evidence" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/requests/build_from_evidence_valid.json)
echo "$BUILD_RESP" | jq .
BUILD_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL/gateway/build-from-evidence" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/requests/build_from_evidence_valid.json)
echo "HTTP $BUILD_CODE"
if [ "$BUILD_CODE" != "200" ]; then
  echo "FAIL: build-from-evidence should return 200"
  echo "ERROR DETAIL: $(echo "$BUILD_RESP" | jq -r '.errors[0].message // "unknown"' 2>/dev/null)"
  FAIL=1
fi
BUILD_ACCEPTED=$(echo "$BUILD_RESP" | jq -r '.accepted // false')
BUILD_CREATED=$(echo "$BUILD_RESP" | jq -r '.issue_created // "unknown"')
if [ "$BUILD_ACCEPTED" != "true" ]; then
  echo "FAIL: build-from-evidence should be accepted"
  FAIL=1
fi
if [ "$BUILD_CREATED" != "false" ]; then
  echo "FAIL: build-from-evidence default must not create issue"
  FAIL=1
fi

echo ""
echo "=== Preflight: valid payload ==="
VALID_RESP=$(curl -s -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/gateway/valid_verification_report_candidate.json)
echo "$VALID_RESP" | jq .
VALID_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/gateway/valid_verification_report_candidate.json)
echo "HTTP $VALID_CODE"
if [ "$VALID_CODE" != "200" ]; then
  echo "FAIL: valid payload preflight should return 200"
  FAIL=1
fi
ACCEPTED=$(echo "$VALID_RESP" | jq -r '.accepted // false')
CREATED=$(echo "$VALID_RESP" | jq -r '.issue_created // "unknown"')
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
INVALID_RESP=$(curl -s -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/gateway/invalid_issue_151_style_payload.json)
echo "$INVALID_RESP" | jq .
INVALID_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$GATEWAY_URL/gateway/preflight" \
  -H "Content-Type: application/json" \
  --data @tests/fixtures/gateway/invalid_issue_151_style_payload.json)
echo "HTTP $INVALID_CODE"
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
