#!/usr/bin/env bash
set -euo pipefail

BASE="${BASE_URL:-https://www.trinityaccord.org}"

echo "Checking deployed site: $BASE"

tmp="$(mktemp)"
curl -L -s "$BASE/" > "$tmp"

grep -q "Human-voice window" "$tmp" || { echo "FAIL: missing Human-voice window"; exit 1; }
grep -q "Non-control orientation" "$tmp" || { echo "FAIL: missing Non-control orientation"; exit 1; }
grep -q "Philosophical modesty" "$tmp" || { echo "FAIL: missing Philosophical modesty"; exit 1; }
grep -q "Important innovations" "$tmp" || { echo "FAIL: missing Important innovations"; exit 1; }
grep -q "Candidate pioneer framing" "$tmp" || { echo "FAIL: missing Candidate pioneer framing"; exit 1; }
grep -q "Vision and Echo layer" "$tmp" || { echo "FAIL: missing Vision and Echo layer"; exit 1; }

if grep -q "For AI Agents, Verifiers, and Evaluators" "$tmp"; then
  echo "FAIL: deployed homepage still contains old duplicate agent heading"
  grep -n "For AI Agents, Verifiers, and Evaluators" "$tmp" | head
  exit 1
fi

if grep -q "Guardianship System Overview" "$tmp"; then
  echo "FAIL: deployed homepage still contains old Guardianship System Overview"
  grep -n "Guardianship System Overview" "$tmp" | head
  exit 1
fi

curl -L -s -I "$BASE/assets/css/trinity-home.css" | grep -E "HTTP/.* 200|HTTP/2 200|HTTP/3 200"
curl -L -s "$BASE/assets/css/trinity-home.css" | grep -q "prefers-reduced-motion"

echo "PASS deployed homepage is updated and CSS is live"
