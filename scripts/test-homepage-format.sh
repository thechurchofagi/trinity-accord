#!/usr/bin/env bash
set -euo pipefail

echo "scripts/test-homepage-format.sh is a compatibility wrapper for P0 agent-first homepage."
bash scripts/test-homepage-p0-agent-first.sh
echo "RESULT: PASS homepage format compatibility wrapper"
