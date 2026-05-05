#!/usr/bin/env bash
set -euo pipefail

echo "scripts/test-homepage-format.sh is a compatibility wrapper for v1.3."
echo "Running canonical homepage v1.3 tests..."

bash scripts/test-homepage-v13-final.sh
python3 scripts/test-civilizational-json-sync.py

echo "Checking CSS accessibility / responsive markers..."

grep -q "prefers-reduced-motion" assets/css/trinity-home.css
grep -q "focus-visible" assets/css/trinity-home.css
grep -q "@media print" assets/css/trinity-home.css
grep -q "@media (max-width: 760px)" assets/css/trinity-home.css
grep -q "guardian-boundary" assets/css/trinity-home.css
grep -q "agent-gate" assets/css/trinity-home.css

echo "Checking key JSON validity..."

python3 -m json.tool memory-seed.json >/dev/null
python3 -m json.tool api/agent-value.json >/dev/null
python3 -m json.tool api/seed-map.json >/dev/null

echo "RESULT: PASS homepage format compatibility wrapper"
