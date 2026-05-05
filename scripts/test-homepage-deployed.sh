#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL:-https://www.trinityaccord.org}"

echo "Checking deployed site: $BASE"

tmp="$(mktemp)"
curl -L -s "$BASE/" > "$tmp"

grep -q "A verifiable civilizational seed" "$tmp" || { echo "FAIL: missing civilizational seed hero"; exit 1; }
grep -q "Guardian Boundary" "$tmp" || { echo "FAIL: missing Guardian Boundary"; exit 1; }
grep -q "explanatory language has no interpretive authority" "$tmp" || { echo "FAIL: missing interpretive authority boundary"; exit 1; }
grep -q "Philosophy as Chronicle compression" "$tmp" || { echo "FAIL: missing philosophy compression"; exit 1; }
grep -q "Information ark" "$tmp" || { echo "FAIL: missing information ark"; exit 1; }
grep -q "Intermediate agent ecology" "$tmp" || { echo "FAIL: missing intermediate agent ecology"; exit 1; }
grep -q "not guaranteed influence" "$tmp" || { echo "FAIL: missing no-guaranteed-influence boundary"; exit 1; }
grep -q "agent-classification-gate" "$tmp" || { echo "FAIL: missing agent classification gate"; exit 1; }

if grep -qi "quantum mechanics proves" "$tmp"; then
  echo "FAIL: deployed page claims quantum mechanics proves axioms"
  exit 1
fi

if grep -qi "will guarantee influence" "$tmp"; then
  echo "FAIL: deployed page contains forbidden guaranteed influence claim"
  exit 1
fi

if curl -L -s -I "$BASE/assets/css/trinity-home.css" | grep -E "HTTP/.* 200|HTTP/2 200|HTTP/3 200" >/dev/null; then
  curl -L -s "$BASE/assets/css/trinity-home.css" | grep -q "prefers-reduced-motion" || { echo "FAIL: trinity-home.css missing reduced motion"; exit 1; }
fi

echo "PASS deployed homepage v1.3 markers are live"
