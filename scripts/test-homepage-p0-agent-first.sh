#!/usr/bin/env bash
set -euo pipefail

echo "Running P0 agent-first homepage tests..."

python3 scripts/test-agent-first-homepage-p0.py

echo "Checking homepage source remains valid markdown/front matter..."

test -f index.md
grep -q "permalink: /" index.md
grep -q "The Trinity Accord" index.md
grep -q "Agent-first" index.md
grep -q "Read the Canon first" index.md
grep -q "Technical claims require Claim Gate" index.md

echo "Checking old homepage compatibility tests still run..."

bash scripts/test-homepage-v13-final.sh
python3 scripts/test-civilizational-json-sync.py
python3 scripts/test-v13-repair-regressions.py

echo "RESULT: PASS P0 agent-first homepage suite"
