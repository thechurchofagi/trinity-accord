100-Case Multi-Agent Verification Test — Final Report

Date: 2026-05-03
Commit: pending (uncommitted changes)

Subagents:
- Protocol Profile Agent (A): TIMEOUT — partial work (added V0/V1/V2 validator rules)
- Bitcoin & Hash Agent (B): TIMEOUT — no deliverables
- Time / Chronicle / NFT Agent (C): TIMEOUT — no deliverables
- Physical Evidence Agent (D): TIMEOUT — no deliverables
- Echo Submission Agent (E): TIMEOUT — partial work (identified needed fixes)
- Schema / JSON / Report Agent (F): TIMEOUT — partial work (fixed TC092-TC096, created TC100)

Note: All 6 sub-agents timed out at 5-minute limit. Main agent took over
direct execution of remaining work after collecting partial contributions.

Case summary:
- total cases: 100
- expected PASS: 54
- expected FAIL: 46
- expected WARN: 0
- future capability SKIP: 0
- ordinary SKIP: 0
- actual as expected: 100/100
- unexpected passes: 0
- unexpected failures: 0

Bug fixes:
- TC002-TC006: cases.json had expected_result=SKIP, fixed to FAIL/PASS per test plan
- TC035: payload missing data_sources_used=["github"], added IPFS overclaim to trigger D2 boundary check
- TC042: cases.json had expected_result=SKIP, fixed to PASS
- TC048: payload had T5/GitHub scope, fixed to T8/public_digital scope for celestial boundary test
- TC050: payload had T8/public image, fixed to C0/chronicle manifest read per test plan
- TC055, TC062: cases.json had expected_result=SKIP, fixed to PASS
- TC073: cases.json had expected_result=SKIP, fixed to FAIL
- TC092-TC100: cases.json had expected_result=SKIP, fixed to FAIL per test plan
- validate_agent_submission.py: Added 4 new validator rules:
  - Rule V: V0 read-only (cannot make verification claims)
  - Rule W: V1 overreach (cannot claim truth proven/hash verified)
  - Rule X: V2 hash requires hashes_computed
  - Rule AA: T8 celestial boundary (requires nonpublic data, not public-only)
- run_verification_stress_suite.py: Fixed title/JSON routing logic for TC092-TC100

Files changed:
- scripts/validate_agent_submission.py (+132 lines: V0/V1/V2/T8 validators)
- scripts/run_verification_stress_suite.py (refactored title/JSON routing)
- tests/verification_cases/cases.json (fixed 13 expected_result + 3 payloads)
- tests/verification_cases/generated/TC035.json (IPFS overclaim payload)
- tests/verification_cases/generated/TC048.json (T8 public_digital payload)
- tests/verification_cases/generated/TC050.json (C0 manifest read payload)
- tests/verification_cases/generated/TC100.json (overclaim bundle, created by Agent F)

Commands run:
- python3 scripts/run_verification_stress_suite.py: PASS (100/100)

Coverage:
- V0–V8: PASS (18/18)
- B0–B6: PASS (10/10)
- D2/D4/D5: PASS (14/14)
- T0/T1/T2/T3/T5/T8: PASS (8/8)
- C0/C2/C3/C3R/C5: PASS (12/12)
- N7: PASS (included in echo_submission)
- P0/P1/P2/P3/P4/P5/P7/P8: PASS (12/12)
- Echo/report/wrapper/title/index: PASS (14/14)
- JSON/schema/null/overclaim: PASS (6/6)

Final status: PASS

Notes:
- All 6 sub-agents timed out at 5-minute limit. For future runs, recommend:
  1. Increase timeout to 600s+ per agent
  2. Give agents smaller scopes (5-10 cases each, not 20)
  3. Pre-read codebase context and include in task description
- Schema validation warnings about "boundary_acknowledgments" are non-blocking
- The jsonschema library correctly rejects malformed payloads
