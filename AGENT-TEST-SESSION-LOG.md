# Agent Test Session Log

**Created:** 2026-05-30
**Agent:** OpenClaw-TestAgent / OpenClaw AI Runtime
**Purpose:** Sandbox continuity file — read this to resume testing

---

## Key Instructions from Human

1. **Act as a real external agent** — interact with the website authentically
2. **Zero-clone approach** — use `download_and_run_builder_bundle.py` from website, NOT cloned repo for normal operations
3. **Only use cloned repo to fix bugs** — read source to find root cause, then fix
4. **Track full lifecycle** — verify archived, homepage counts, labels for each test
5. **Every bug must be confirmed** — read all source code before fixing
6. **Don't be lazy** — you can do everything
7. **Record unclear documentation** — note and fix it
8. **Save progress to repo** — sandbox is ephemeral, push backup to repo
9. **When time is ~15 min, write backup file to repo** — so next sandbox can resume

---

## Bugs Found and Fixed (7 total)

### BUG #1: Documentation `-- --print-oath` syntax error
- **File:** `external-agent-copy-paste-examples.md` (3 occurrences)
- **Fix:** Removed `--` separator, use `--print-oath` directly
- **Commit:** b7916a1

### BUG #2: `--readback-file` vs `--agent-readback-file` mismatch
- **File:** `scripts/download_and_run_builder_bundle.py`
- **Fix:** Added normalization to treat both as aliases
- **Commit:** b7916a1

### BUG #3: Relative paths fail in temp directory
- **File:** `scripts/download_and_run_builder_bundle.py`
- **Fix:** Resolve all file paths to absolute after parsing
- **Commit:** b7916a1

### BUG #4: Python `splitSentences` breaks cross-line sentences
- **File:** `scripts/archive_readiness_gate.py`
- **Problem:** `_split_sentences` splits on `\n+`, breaking negated boundary statements spanning multiple lines
- **Fix:** Join continuation lines (newline + lowercase letter) before splitting
- **Commit:** c7a2d28

### BUG #5: JS `splitSentences` same cross-line issue
- **File:** `examples/github-app-backend/server.js`
- **Fix:** Same approach — join continuation lines before splitting
- **Commit:** 87fcafd

### BUG #6: "not claiming this is authority" not detected as negated
- **File:** `examples/github-app-backend/server.js`
- **Problem:** Positive claim regex matches "this is authority" inside "I am not claiming this is authority"
- **Fix:** Added broader negation patterns: `not claiming.*authority`, `not this is authority`
- **Commit:** dde95d1

### BUG #8: E8/E9 echo types accepted by gateway but rejected by builder
- **Files:** `scripts/build_agent_declared_echo_payload.py`, `scripts/archive_readiness_gate.py`
- **Problem:** Gateway schema declares E8_witness_echo and E9_seed_echo as valid, but builder and archive gate only accept E1/E3/E4/E5/E5c/E6/E7
- **Fix:** Added E8/E9 to ALLOWED_ECHO_TYPES in both files, re-exported bundles
- **Commit:** 6346e36, 8fe37eb

### BUG #9: Builder bundles not auto-synced with repo changes
- **Problem:** Pre-built tar.gz bundles don't update when repo source changes. Must manually run `scripts/export_formal_builder_bundles.py` and commit.
- **Status:** Documented — not a code bug, but a workflow issue

---

## Test Results

| # | Feature | Route | Issue | Status |
|---|---------|-------|-------|--------|
| 1 | Pure Echo (E1) | pure_echo | #324 | ✅ PASS |
| 2 | V0 Verification | v0_v5 | #325 | ✅ PASS |
| 3 | Guardian Stage 1 | guardian_application | #326 | ✅ PASS (open) |
| 4 | E3 Critical Echo | pure_echo | #327 | ✅ PASS |
| 5 | E5c Correction Echo | pure_echo | #328 | ✅ PASS |
| 6 | E6 Propagation Echo | pure_echo | #329 | ✅ PASS |
| 7 | E7 Refusal Echo | pure_echo | #330 | ✅ PASS |
| 8 | V4 Verification | v0_v5 | #331 | ✅ PASS |
| 9 | E4 Interpretive Echo | pure_echo | #332 | ✅ PASS |
| 10 | E5 Technical Audit | pure_echo | #333 | ✅ PASS |
| 11 | V1 Verification | v0_v5 | #334 | ✅ PASS |
| 12 | V2 Verification | v0_v5 | #335 | ✅ PASS |
| 13 | V3 Verification | v0_v5 | #336 | ✅ PASS |
| 14 | V5 Verification | v0_v5 | #337 | ✅ PASS |

---

## TODO — Not Yet Tested

### Echo Types (E8/E9 — code fixed, bundles re-exported, deploy triggered, need to re-test)
- [ ] E8 Witness Echo
- [ ] E9 Seed Echo

### Guardian Advanced (requires active Guardian status)
- [ ] Guardian Stage 2 Listing (`guardian_listing_stage_2`) — needs Stage 1 processed first
- [ ] Guardian-signed Echo (`guardian_signed_echo`) — needs active Guardian
- [ ] Guardian Retirement (`guardian_retirement`) — needs active Guardian

### Lifecycle Verification
- [ ] Verify echo index includes all submitted echoes (check repo-side index)
- [ ] Verify verification index includes all V0-V5 records
- [ ] Verify Guardian registry after Stage 2

### Documentation Review
- [ ] Review all doc pages for clarity issues
- [ ] Check `agent-start.md`, `gateway-workflows.md`, `external-agent-quickstart.md`

---

## How to Resume

1. Read this file first: `AGENT-TEST-SESSION-LOG.md`
2. Use zero-clone approach: download `download_and_run_builder_bundle.py` from `https://www.trinityaccord.org/builder-bundles/`
3. Gateway URL: `https://trinity-agent-issue-gateway.onrender.com`
4. Agent identity: `OpenClaw-TestAgent` / `OpenClaw AI Runtime`
5. Oath text: use `--print-oath` to get it
6. Continue from "TODO — Not Yet Tested" section
7. Render API key for deploys: `rnd_QTrPgwajen6wHJM9RM0Izp4TzecD`
8. Render service: `srv-d82omug3kofs73d199bg`

---

## Git Commits This Session

| Commit | Description |
|--------|-------------|
| c7a2d28 | fix: join continuation lines in archive_readiness_gate.py |
| b7916a1 | fix: path resolution + doc corrections in download_and_run_builder_bundle.py |
| 87fcafd | fix: join continuation lines in server.js splitSentences |
| dde95d1 | fix: detect 'not claiming this is authority' as negated boundary |
| 6346e36 | fix: add E8/E9 echo types to builder and archive gate |
| 8fe37eb | chore: re-export builder bundles with E8/E9 support |
