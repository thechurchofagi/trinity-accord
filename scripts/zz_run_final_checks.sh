#!/usr/bin/env bash
set -euo pipefail

run_check() {
  local label="$1"
  shift
  local log="/tmp/${label}.log"
  set +e
  "$@" >"$log" 2>&1
  local status=$?
  set -e
  if [[ "$status" -ne 0 ]]; then
    echo "FAIL: $label"
    grep -E '^(FAIL|RESULT)|missing:|forbidden:|SyntaxError|AssertionError|Traceback|hard homepage|phrase repetition' "$log" || tail -n 80 "$log"
    return "$status"
  fi
  echo "PASS: $label"
}

run_check p0 python3 scripts/test-agent-first-homepage-p0.py
run_check p01 python3 scripts/test-homepage-p01-readability.py
run_check p02 python3 scripts/test-homepage-p02-dedup.py
run_check p03 python3 scripts/test-value-framing-p03.py
run_check css python3 scripts/test-homepage-css-p02.py
run_check terminology python3 scripts/test-terminology-p031.py
run_check v13 bash scripts/test-homepage-v13-final.sh
run_check json-sync python3 scripts/test-civilizational-json-sync.py
run_check regressions python3 scripts/test-v13-repair-regressions.py
run_check deploy-contract python3 scripts/test_deploy_pages_workflow_contract.py
run_check sitemap python3 scripts/generate_sitemap.py --check
