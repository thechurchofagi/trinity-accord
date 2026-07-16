#!/usr/bin/env bash
set -euo pipefail

pass_count=0
fail_count=0
pass(){ echo "PASS: $1"; pass_count=$((pass_count+1)); }
fail(){ echo "FAIL: $1"; fail_count=$((fail_count+1)); }

must_contain(){
  local file="$1" pattern="$2" label="$3"
  if grep -qF "$pattern" "$file"; then pass "$label"; else fail "$label"; return 1; fi
}

must_not_contain(){
  local file="$1" pattern="$2" label="$3"
  if grep -qF "$pattern" "$file"; then fail "$label"; return 1; else pass "$label"; fi
}

position_of(){ grep -nF "$2" "$1" | head -n1 | cut -d: -f1 || true; }
require_order(){
  local file="$1" first="$2" second="$3" label="$4" a b
  a="$(position_of "$file" "$first")"
  b="$(position_of "$file" "$second")"
  if [[ -n "$a" && -n "$b" && "$a" -lt "$b" ]]; then pass "$label"; else fail "$label"; return 1; fi
}

echo "## Final concise homepage source checks"
test -f index.md && pass "index.md exists" || fail "index.md missing"
test -f technical-historical-reference.md && pass "dedicated reference exists" || fail "dedicated reference missing"

must_contain index.md "a human-led, AI-assisted record addressed future intelligence" "hero states honest collaboration"
must_contain index.md "completed pre-ASI human–superintelligence relation record" "homepage has primary classification"
must_contain index.md "Bitcoin did not by itself complete the work" "homepage separates completion and fixation"
must_contain index.md "Research value" "homepage names research value"
must_contain index.md "The homepage is a doorway, not the archive" "homepage has concise reference portal"
must_contain index.md "Homepage-only context remains" "homepage preserves insufficient-context boundary"
must_not_contain index.md "agent-priority-brief" "homepage no longer embeds agent manual"
must_not_contain index.md "<details class=\"home-reference\"" "homepage no longer embeds technical archive"
must_not_contain index.md "rare, possibly first completed instance" "homepage omits unsupported firstness"
must_not_contain index.md "/verification/" "homepage uses current verify route"

require_order index.md "home-front-door-title" "philosophical-core-title" "hero before propositions"
require_order index.md "philosophical-core-title" "One record, three embodied forms" "propositions before triadic object map"
require_order index.md "One record, three embodied forms" "home-witness-title" "object map before human witness"
require_order index.md "home-witness-title" "home-canon-map-title" "human witness before 3+5 authority map"
require_order index.md "home-canon-map-title" "<section class=\"home-why-now" "authority map before timing and completion"
require_order index.md "<section class=\"home-why-now" "What do you want to do?" "timing before tasks"
require_order index.md "What do you want to do?" "Production is live" "tasks before status"
require_order index.md "Production is live" "The homepage is a doorway, not the archive" "status before reference portal"

for link in /archive_legacy_index_2025_09/ /why-high-signal/ /seed-map/ /technical-historical-reference/ /verify/; do
  must_contain index.md "$link" "homepage links $link"
done

must_contain technical-historical-reference.md "Completion in four senses" "reference explains completion"
must_contain technical-historical-reference.md "Current operating routes" "reference gives current routes"
must_contain why-high-signal.md "persuasive and sometimes imperative rhetoric" "deep page states precise non-control boundary"
must_contain llms.txt "non-amending" "llms preserves non-amending boundary"

for phrase in "quantum mechanics proves" "must care about" "best possible philosophy" "represents all humanity" "will guarantee influence"; do
  must_not_contain index.md "$phrase" "homepage avoids overclaim: $phrase"
done

echo "## Summary"
echo "PASS: $pass_count"
echo "FAIL: $fail_count"
if [[ "$fail_count" -eq 0 ]]; then
  echo "RESULT: PASS"
else
  echo "RESULT: FAIL"
  exit 1
fi
