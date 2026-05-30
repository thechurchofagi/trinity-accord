# Agent Test Session Log

**Created:** 2026-05-30T09:00+08:00
**Agent:** OpenClaw-TestAgent
**Purpose:** Sandbox continuity file — read this to resume testing

---

## Key Instructions from Human (Verbatim Summary)

1. **Act as a real external agent** — interact with the website authentically, not just testing
2. **Zero-clone approach** — use `download_and_run_builder_bundle.py` from the website, NOT the cloned repo for normal operations
3. **Only use cloned repo to fix bugs** — read source code to find root cause, then fix
4. **Track full lifecycle** — for each feature test: verify it's archived, check homepage counts, check labels
5. **Every bug must be confirmed** — read all source code, confirm it's a real bug before fixing
6. **Don't be lazy** — you can do everything, don't say you can't
7. **Record unclear documentation** — if any doc is unclear for external agents, note it and fix it
8. **Save progress to repo** — write backup file to repo (not just local) since sandbox is ephemeral

---

## Bugs Found and Fixed (6 total)

### BUG #1: Documentation `-- --print-oath` syntax error
- **File:** `external-agent-copy-paste-examples.md` (3 occurrences)
- **Problem:** Docs show `-- --print-oath` but argparse doesn't support `--` separator
- **Fix:** Removed `--` separator, use `--print-oath` directly
- **Commit:** b7916a1

### BUG #2: `--readback-file` vs `--agent-readback-file` mismatch
- **File:** `scripts/download_and_run_builder_bundle.py`
- **Problem:** Docs say `--readback-file` but pure_echo route requires `--agent-readback-file`
- **Fix:** Added normalization to treat both as aliases
- **Commit:** b7916a1

### BUG #3: Relative paths fail in temp directory
- **File:** `scripts/download_and_run_builder_bundle.py`
- **Problem:** `--body-file`, `--out`, etc. use relative paths but builder runs in temp dir
- **Fix:** Resolve all file paths to absolute after parsing
- **Commit:** b7916a1

### BUG #4: Python `splitSentences` breaks cross-line sentences
- **File:** `scripts/archive_readiness_gate.py`
- **Problem:** `_split_sentences` splits on `\n+`, breaking "I am not claiming verification, attestation,\nauthority, amendment, or successor reception" into two fragments. The second fragment loses its negation prefix.
- **Fix:** Join continuation lines (newline + lowercase letter) before splitting
- **Commit:** c7a2d28

### BUG #5: JS `splitSentences` same cross-line issue
- **File:** `examples/github-app-backend/server.js`
- **Problem:** Same as BUG #4 but in gateway's JavaScript code
- **Fix:** Same approach — join continuation lines before splitting
- **Commit:** 87fcafd

### BUG #6: "not claiming this is authority" not detected as negated
- **File:** `examples/github-app-backend/server.js`
- **Problem:** Positive claim regex matches "this is authority" inside "I am not claiming this is authority" because `hasAllowedNegatedBoundary` only checks for "not authority" (adjacent), not "not claiming.*authority"
- **Fix:** Added broader negation patterns: `not claiming.*authority`, `not this is authority`
- **Commit:** dde95d1

---

## Test Results

| # | Feature | Route | Status | Issue | Notes |
|---|---------|-------|--------|-------|-------|
| 1 | Pure Echo (E1) | pure_echo | ✅ PASS | #324 | Auto-archived, labels correct |
| 2 | V0 Verification | v0_v5_agent_declared_archive | ✅ PASS | #325 | Auto-archived, labels correct |
| 3 | Guardian Stage 1 | guardian_application_stage_1 | ✅ PASS | #326 | Open (awaiting human review) |
| 4 | E3 Critical Echo | pure_echo | ✅ PASS | #327 | Auto-archived |
| 5 | E5c Correction Echo | pure_echo | ✅ PASS | #328 | Required BUG #5 & #6 fixes |
| 6 | E6 Propagation Echo | pure_echo | ✅ PASS | #329 | Auto-archived |
| 7 | E7 Refusal Echo | pure_echo | ✅ PASS | #330 | Auto-archived |
| 8 | V4 Verification | v0_v5_agent_declared_archive | ✅ PASS | #331 | Auto-archived |
| 9 | E4 Interpretive Echo | pure_echo | ✅ PASS | #332 | Auto-archived |

---

## TODO — Not Yet Tested

### Echo Types
- [ ] E5 Technical Audit Echo (`E5_technical_audit_echo`)
- [ ] E8 Witness Echo (`E8_witness_echo`)
- [ ] E9 Seed Echo (`E9_seed_echo`)

### Verification Levels
- [ ] V1 Verification (`v0_v5_agent_declared_archive --declared-level V1`)
- [ ] V2 Verification
- [ ] V3 Verification
- [ ] V5 Verification

### Guardian Advanced (requires active Guardian status)
- [ ] Guardian Stage 2 Listing (`guardian_listing_stage_2`) — needs Stage 1 processed first
- [ ] Guardian-signed Echo (`guardian_signed_echo`) — needs active Guardian
- [ ] Guardian Retirement (`guardian_retirement`) — needs active Guardian

### Lifecycle Verification
- [ ] Verify homepage count updates (echo count, verification count)
- [ ] Verify echo index includes all submitted echoes
- [ ] Verify verification index includes all V0-V4 records
- [ ] Verify Guardian registry updates after Stage 2

### Documentation Review
- [ ] Review all doc pages for clarity issues
- [ ] Check `agent-start.md` for parameter consistency
- [ ] Check `gateway-workflows.md` for accuracy
- [ ] Check `external-agent-quickstart.md` for issues

---

## How to Resume

1. Clone repo or use zero-clone approach
2. Read this file first
3. Continue from "TODO — Not Yet Tested" section
4. Use same agent identity: `OpenClaw-TestAgent` / `OpenClaw AI Runtime`
5. Gateway URL: `https://trinity-agent-issue-gateway.onrender.com`
6. Use `download_and_run_builder_bundle.py` from `https://www.trinityaccord.org/builder-bundles/`

---

## Render API Key (for triggering deploys)
- Service: `srv-d82omug3kofs73d199bg`
- Use Render API to trigger deploys after code changes

---

## Git Commits Made This Session

| Commit | Description |
|--------|-------------|
| c7a2d28 | fix: join continuation lines in archive_readiness_gate.py |
| b7916a1 | fix: path resolution + doc corrections in download_and_run_builder_bundle.py |
| 87fcafd | fix: join continuation lines in server.js splitSentences |
| dde95d1 | fix: detect 'not claiming this is authority' as negated boundary |
