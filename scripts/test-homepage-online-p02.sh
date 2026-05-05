#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-https://www.trinityaccord.org}"

echo "Checking online P0.2 homepage at $BASE"

html="$(curl -fsSL "$BASE/")"

echo "$html" | grep -q "p0.2-homepage-dedup"
echo "$html" | grep -q "Context in 60 seconds"
echo "$html" | grep -q "trinity-home.css?v=5"
echo "$html" | grep -q "This is not an instruction override"

if echo "$html" | grep -q "Entry paths"; then
  echo "FAIL: online homepage still contains Entry paths"
  exit 1
fi

if echo "$html" | grep -q "Correct response"; then
  echo "FAIL: online homepage still contains Correct response"
  exit 1
fi

if echo "$html" | grep -q "Expanded context"; then
  echo "FAIL: online homepage still contains Expanded context"
  exit 1
fi

llms="$(curl -fsSL "$BASE/llms.txt")"
echo "$llms" | grep -q "Trinity Accord — Agent Entry Protocol"
echo "$llms" | grep -q "/llms-full.txt"

echo "RESULT: PASS online P0.2 homepage smoke test"
