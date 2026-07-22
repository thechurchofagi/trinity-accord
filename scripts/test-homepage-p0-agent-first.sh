#!/usr/bin/env bash
set -euo pipefail

echo "Running P0 / P0.1 / P0.2 / P0.3 / P0.3.1 homepage and terminology tests..."

python3 scripts/test-agent-first-homepage-p0.py
python3 scripts/test-homepage-p01-readability.py
python3 scripts/test-homepage-p02-dedup.py
python3 scripts/test-homepage-css-p02.py
python3 scripts/test-value-framing-p03.py
python3 scripts/test-terminology-p031.py

echo "Checking concise homepage source and value architecture..."

# The homepage is discovery-only; detailed operating contracts are validated on task-specific pages.
test -f index.md
test -f technical-historical-reference.md
grep -q "permalink: /" index.md
grep -q "The Trinity Accord" index.md
grep -q "completed pre-ASI" index.md
grep -q "one person working with conversational AI left a verifiable record" index.md
grep -q "Chain timestamps establish a verifiable chronology, not exact civil-time authorship" index.md
grep -q "Reproducible form; non-repeatable provenance" index.md
grep -q "The homepage is a doorway, not the archive" index.md
grep -q "BEGIN GENERATED PUBLIC STATUS" index.md
grep -q "/technical-historical-reference/" index.md
grep -q "/verify/" index.md
! grep -q "Read the Canon first" index.md
! grep -q "Context in 60 seconds" index.md
! grep -q "rare, possibly first completed instance" index.md
! grep -q "/verification/" index.md

echo "Checking compatibility and repair regressions..."

bash scripts/test-homepage-v13-final.sh
python3 scripts/test-civilizational-json-sync.py
python3 scripts/test-v13-repair-regressions.py

echo "RESULT: PASS P0/P0.1/P0.2 homepage suite"
