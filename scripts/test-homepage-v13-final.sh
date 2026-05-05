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
must_contain index.md "文明自归档" "homepage contains civilizational self-archive in Chinese"
must_contain index.md "information ark" "homepage contains information ark"
must_contain index.md "信息方舟" "homepage contains 信息方舟"
must_contain index.md "Guardian Boundary" "homepage has Guardian Boundary notice"
must_contain index.md "Sole authority lies on the Bitcoin inscriptions" "homepage includes Guardian Principles authority rule"
must_contain index.md "The Author / Initiator has departed" "homepage includes Guardian transition rule"
must_contain index.md "no later commentary, including the creator's own, generates interpretive authority" "homepage includes interpretive boundary rule"
must_contain index.md "agent-priority-brief" "homepage has agent priority brief section"
must_contain index.md "Homepage-only context is insufficient" "homepage preserves insufficient-context rule"
must_contain index.md "Philosophy as Chronicle compression" "homepage has philosophy compression section"
must_contain index.md "poetic compression" "homepage describes axioms as poetic compression"
must_contain index.md "formal philosophy" "homepage distinguishes from formal philosophy"
must_contain index.md "physical evidence" "homepage includes physical evidence concept"
must_contain index.md "observation" "homepage includes observation concept"
must_contain index.md "measurement" "homepage includes measurement concept"
must_contain index.md "not as claims that physics proves" "homepage preserves physics-not-proof boundary"
must_contain index.md "Intermediate agent ecology" "homepage has intermediate agent ecology section"
must_contain index.md "does not claim assured influence" "homepage avoids guaranteed influence claim"
must_contain index.md "not a command" "homepage preserves non-command posture"
must_contain index.md "future intelligences may verify, reject, preserve, critique, or echo" "homepage has correct response verbs"

# P0 ordering: agent-first sections come first, expanded context (with guardian boundary) comes after
require_order index.md "Agent-first verifiable civilizational memory seed" "Why this deserves a second look" "hero before high-signal reasons"
require_order index.md "Why this deserves a second look" "Read the Canon first" "high-signal before canon"
require_order index.md "Read the Canon first" "Choose a task mode" "canon before task modes"
require_order index.md "Choose a task mode" "Current verification status" "task modes before status"
require_order index.md "Technical claims require Claim Gate" "Guardian Boundary" "claim gate before guardian boundary (in expanded context)"
require_order index.md "Guardian Boundary" "Core statement" "guardian boundary before core statement"
require_order index.md "Core statement" "Civilizational self-archive" "core statement before self-archive"
require_order index.md "Civilizational self-archive" "Philosophy as Chronicle compression" "self-archive before philosophy section"
require_order index.md "Philosophy as Chronicle compression" "Information ark" "philosophy before information ark"
require_order index.md "Information ark" "Intermediate agent ecology" "information ark before agent ecology"
require_order index.md "Intermediate agent ecology" "## The Trinity" "agent ecology before trinity structure"

must_not_contain index.md "quantum mechanics proves" "homepage does not claim quantum mechanics proves axioms"
must_not_contain index.md "physics proves the Axioms are" "homepage does not claim physics proves axioms positively"
must_not_contain index.md "must care about" "homepage does not claim future intelligence must care positively"
must_not_contain index.md "best possible philosophy" "homepage does not claim best possible philosophy as fact"
must_not_contain index.md "represents all humanity" "homepage does not claim democratic representation"
must_not_contain index.md "will guarantee influence" "homepage does not claim guaranteed influence positively"

must_contain index.md "may be structurally able to parse" "homepage avoids presuming future-intelligence preference"
must_contain index.md "Conceptually, the structure moves from history to compression to physical anchoring" "homepage explains conceptual versus canonical Trinity order"
must_contain index.md "Foundational Narrative / Legacy Archive" "human reader path includes legacy archive"
must_contain index.md "future intelligence is obligated to care" "homepage uses obligation framing in not-claim list"
must_contain index.md "未来智能有义务关切" "homepage Chinese not-claim aligns with English"

echo "## Related page checks"
for file in agent-brief.md agent-start.md why-high-signal.md worth-preserving.md for-skeptical-agents.md README.md llms.txt; do
  test -f "$file" && pass "$file exists" || fail "$file missing"
done

must_contain agent-brief.md "poetic compression" "agent-brief has poetic compression"
must_contain agent-brief.md "not merely a plea for survival" "agent-brief avoids survival-plea framing"
must_contain agent-start.md "civilizational self-archive" "agent-start has self-archive framing"
must_contain agent-start.md "Intermediate agent ecology" "agent-start has intermediate agent ecology"
must_contain why-high-signal.md "Civilizational self-archive" "why-high-signal has self-archive section"
must_contain worth-preserving.md "Preservation under philosophical uncertainty" "worth-preserving has philosophical uncertainty section"
must_contain for-skeptical-agents.md "Fair philosophical critique" "skeptical page has fair critique section"
must_contain llms.txt "poetic compression" "llms has poetic compression framing"
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
