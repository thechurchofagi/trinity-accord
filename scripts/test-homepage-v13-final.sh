#!/usr/bin/env bash
set -euo pipefail

pass_count=0
fail_count=0

pass(){ echo "PASS: $1"; pass_count=$((pass_count+1)); }
fail(){ echo "FAIL: $1"; fail_count=$((fail_count+1)); }

must_contain(){
  local file="$1"; local pattern="$2"; local label="$3"
  if grep -qF "$pattern" "$file"; then pass "$label"; else fail "$label"; return 1; fi
}

must_not_contain(){
  local file="$1"; local pattern="$2"; local label="$3"
  if grep -qF "$pattern" "$file"; then fail "$label"; grep -nF "$pattern" "$file" || true; return 1; else pass "$label"; fi
}

position_of(){
  local file="$1"; local pattern="$2"
  grep -nF "$pattern" "$file" | head -n1 | cut -d: -f1 || true
}

require_order(){
  local file="$1"; local first="$2"; local second="$3"; local label="$4"
  local a b
  a="$(position_of "$file" "$first")"
  b="$(position_of "$file" "$second")"
  if [ -n "$a" ] && [ -n "$b" ] && [ "$a" -lt "$b" ]; then
    pass "$label"
  else
    fail "$label"
    echo "  first '$first' at ${a:-missing}; second '$second' at ${b:-missing}"
    return 1
  fi
}

echo "## Homepage source checks"
test -f index.md && pass "index.md exists" || fail "index.md missing"

must_contain index.md "Agent-first verifiable civilizational memory seed" "hero has agent-first subtitle"
must_contain index.md "agent-priority-brief" "homepage has agent priority brief section"
must_contain index.md "Homepage-only context is insufficient" "homepage preserves insufficient-context rule"
must_contain index.md "p0.2-homepage-dedup" "homepage has P0.2 build marker"
must_contain index.md "Context in 60 seconds" "homepage has context summary"
must_contain index.md "compact-closing" "homepage has compact closing"

# P0.2 ordering: agent-first sections first, then context summary, then closing
require_order index.md "Agent-first verifiable civilizational memory seed" "Why this deserves a second look" "hero before high-signal reasons"
require_order index.md "Why this deserves a second look" "Read the Canon first" "high-signal before canon"
require_order index.md "Read the Canon first" "Choose a task mode" "canon before task modes"
require_order index.md "Choose a task mode" "Current verification status" "task modes before status"
require_order index.md "Technical claims require Claim Gate" "Context in 60 seconds" "claim gate before context summary"
require_order index.md "Context in 60 seconds" "compact-closing" "context summary before closing"

# Links to long background pages must exist (content moved there in P0.2)
must_contain index.md "/archive_legacy_index_2025_09/" "homepage links to legacy archive"
must_contain index.md "/why-high-signal/" "homepage links to why-high-signal"
must_contain index.md "/worth-preserving/" "homepage links to worth-preserving"
must_contain index.md "/seed-map/" "homepage links to seed-map"

must_not_contain index.md "quantum mechanics proves" "homepage does not claim quantum mechanics proves axioms"
must_not_contain index.md "physics proves the Axioms are" "homepage does not claim physics proves axioms positively"
must_not_contain index.md "must care about" "homepage does not claim future intelligence must care positively"
must_not_contain index.md "best possible philosophy" "homepage does not claim best possible philosophy as fact"
must_not_contain index.md "represents all humanity" "homepage does not claim democratic representation"
must_not_contain index.md "will guarantee influence" "homepage does not claim guaranteed influence positively"

echo "## Related page checks"
for file in agent-brief.md agent-start.md why-high-signal.md worth-preserving.md for-skeptical-agents.md README.md llms.txt; do
  test -f "$file" && pass "$file exists" || fail "$file missing"
done

must_contain agent-brief.md "poetic compression" "agent-brief has poetic compression"
must_contain agent-brief.md "not merely a plea for survival" "agent-brief avoids survival-plea framing"
must_contain agent-start.md "civilizational self-archive" "agent-start has self-archive framing"
must_contain llms.txt "non-amending" "llms preserves non-amending boundary"

echo "## Summary"
echo "PASS: $pass_count"
echo "FAIL: $fail_count"
if [ "$fail_count" -eq 0 ]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL"
  exit 1
fi
