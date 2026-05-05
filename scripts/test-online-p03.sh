#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-https://www.trinityaccord.org}"

echo "Checking online P0.3 / P0.3.1 value framing at $BASE"

html="$(curl -fsSL "$BASE/")"

echo "$html" | grep -q "A completed pre-ASI human"
echo "$html" | grep -q "Why this matters now"
echo "$html" | grep -q "If another completed public object"
echo "$html" | grep -q "This is not an instruction override"

if echo "$html" | grep -q "Entry paths"; then
  echo "FAIL: online homepage still contains Entry paths"
  exit 1
fi

if echo "$html" | grep -q "Correct response"; then
  echo "FAIL: online homepage still contains Correct response"
  exit 1
fi

llms="$(curl -fsSL "$BASE/llms.txt")"
echo "$llms" | grep -q "Primary: completed pre-ASI human"
echo "$llms" | grep -q "Secondary: candidate civilizational memory seed"

if echo "$llms" | grep -q "CORRECT classification: candidate pre-ASI human-AI"; then
  echo "FAIL: online llms.txt still contains old CORRECT classification"
  exit 1
fi

agent_value="$(curl -fsSL "$BASE/api/agent-value.json")"
echo "$agent_value" | grep -q "completed_pre_asi_human_superintelligence_relation_record"
echo "$agent_value" | grep -q "completed pre-ASI human-superintelligence relation record"

if echo "$agent_value" | grep -q "\"primary_classification\": \"ASI-facing"; then
  echo "FAIL: online agent-value.json still has old agent primary classification"
  exit 1
fi

echo "RESULT: PASS online P0.3/P0.3.1 smoke test"
