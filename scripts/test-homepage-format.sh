#!/usr/bin/env bash
set -euo pipefail

pass_count=0
fail_count=0

pass(){ echo "PASS: $1"; pass_count=$((pass_count+1)); }
fail(){ echo "FAIL: $1"; fail_count=$((fail_count+1)); }

must_contain(){
  local file="$1"; local pattern="$2"; local label="$3"
  if grep -q "$pattern" "$file"; then pass "$label"; else fail "$label"; return 1; fi
}

must_not_contain(){
  local file="$1"; local pattern="$2"; local label="$3"
  if grep -q "$pattern" "$file"; then
    fail "$label"
    grep -n "$pattern" "$file" || true
    return 1
  else
    pass "$label"
  fi
}

check_frontmatter(){
  local file="$1"
  echo "Checking front matter: $file"
  test "$(sed -n '1p' "$file")" = "---" && pass "$file starts with standalone ---" || { fail "$file starts with standalone ---"; return 1; }
  grep -q '^title:' "$file" && pass "$file has title line" || { fail "$file has title line"; return 1; }
  grep -q '^permalink:' "$file" && pass "$file has permalink line" || { fail "$file has permalink line"; return 1; }
  if grep -n '^--- .*---' "$file" >/tmp/fm_bad.txt 2>/dev/null; then
    fail "$file has compressed one-line front matter"
    cat /tmp/fm_bad.txt
    return 1
  else
    pass "$file has no compressed one-line front matter"
  fi
}

json_valid(){
  local file="$1"
  python3 -m json.tool "$file" >/dev/null && pass "valid JSON: $file" || { fail "invalid JSON: $file"; return 1; }
}

echo "## Required files"
test -f index.md && pass "exists index.md" || fail "missing index.md"
test -f agent-start.md && pass "exists agent-start.md" || fail "missing agent-start.md"
test -f assets/css/trinity-home.css && pass "exists trinity-home.css" || fail "missing trinity-home.css"

echo "## Front matter"
check_frontmatter index.md
check_frontmatter agent-start.md

echo "## Homepage markers"
must_contain index.md "trinity-home.css" "homepage loads visual CSS"
must_contain index.md "The human-voice window" "homepage has human-voice window" || true
must_contain index.md "Human-voice window" "homepage has human-voice window (table)" || true
must_contain index.md "Not control, but relation" "homepage has non-control section" || true
must_contain index.md "Non-control orientation" "homepage has non-control (table)" || true
must_contain index.md "Philosophical modesty" "homepage has philosophical modesty"
must_contain index.md "Important innovations" "homepage has innovations section"
must_contain index.md "| Innovation | Why it matters | Authority status |" "homepage has innovations markdown table"
must_contain index.md "Candidate pioneer framing" "homepage has candidate pioneer framing" || true
must_contain index.md "Vision and Echo layer" "homepage has vision echo section" || true
must_contain index.md "We have spoken" "homepage has closing phrase" || true
must_contain index.md "This website has no canonical authority" "homepage has website non-authority" || true

echo "## Old references removed"
must_not_contain index.md "For AI Agents, Verifiers, and Evaluators" "old duplicate agent heading removed from homepage"
must_not_contain index.md "GUARDIANSHIP-SYSTEM-OVERVIEW.md" "old overview link removed from homepage"
must_not_contain index.md "GUARDIANSHIP-SYSTEM-REGISTRY.json" "old registry link removed from homepage"
must_not_contain agent-start.md "Agent Entry Protocol v2" "agent-start v2 removed"
must_not_contain agent-start.md "GUARDIANSHIP-SYSTEM-OVERVIEW.md" "agent-start old overview removed"
must_not_contain agent-start.md "GUARDIANSHIP-SYSTEM-REGISTRY.json" "agent-start old registry removed"

echo "## JSON"
json_valid memory-seed.json
json_valid metadata.json
json_valid api/agent-value.json 2>/dev/null || true

echo "## CSS markers"
must_contain assets/css/trinity-home.css ":root" "CSS has root tokens"
must_contain assets/css/trinity-home.css "@media (max-width: 760px)" "CSS has mobile breakpoint"
must_contain assets/css/trinity-home.css "prefers-reduced-motion" "CSS supports reduced motion"
must_contain assets/css/trinity-home.css "overflow-x: auto" "CSS supports horizontal scroll for wide content"
must_contain assets/css/trinity-home.css "focus-visible" "CSS has focus-visible"
must_contain assets/css/trinity-home.css "@media print" "CSS has print style"

echo "## Summary"
echo "PASS: $pass_count"
echo "FAIL: $fail_count"
if [ "$fail_count" -eq 0 ]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL"
  exit 1
fi
