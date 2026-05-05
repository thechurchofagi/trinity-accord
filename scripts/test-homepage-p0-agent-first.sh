#!/usr/bin/env bash
set -euo pipefail

echo "Running P0 / P0.1 / P0.2 homepage tests..."

python3 scripts/test-agent-first-homepage-p0.py
python3 scripts/test-homepage-p01-readability.py
python3 scripts/test-homepage-p02-dedup.py
python3 scripts/test-homepage-css-p02.py
python3 scripts/test-value-framing-p03.py

echo "Checking homepage source remains valid markdown/front matter..."

test -f index.md
grep -q "permalink: /" index.md
grep -q "The Trinity Accord" index.md
grep -q "completed pre-ASI" index.md
grep -q "Read the Canon first" index.md
grep -q "Technical claims require Claim Gate" index.md
grep -q "Context in 60 seconds" index.md
grep -q "p0.2-homepage-dedup" index.md
grep -q "completed pre-ASI" index.md
grep -q "Why this matters now" index.md

echo "Checking old homepage compatibility tests still run..."

bash scripts/test-homepage-v13-final.sh
python3 scripts/test-civilizational-json-sync.py
python3 scripts/test-v13-repair-regressions.py

echo "RESULT: PASS P0/P0.1/P0.2 homepage suite"
