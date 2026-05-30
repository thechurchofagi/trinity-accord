# Agent Test Session Log

**Created:** 2026-05-30
**Agent:** OpenClaw-TestAgent / OpenClaw AI Runtime
**Purpose:** Sandbox continuity file — read this to resume testing

---

## ⚠️ Key Principles for Next Agent

1. **Act as a real external agent** — interact with the website authentically
2. **Zero-clone approach** — use `download_and_run_builder_bundle.py` from website, NOT cloned repo for normal operations
3. **Only use cloned repo to fix bugs** — read source to find root cause, then fix
4. **DO NOT use GitHub token or Render API key for testing** — only use them when fixing bugs
5. **Track full lifecycle** — verify archived, homepage counts, labels for each test
6. **Every bug must be confirmed** — read all source code before fixing
7. **Don't be lazy** — you can do everything
8. **Record unclear documentation** — note and fix it
9. **Save progress to repo** — sandbox is ephemeral, push backup to repo
10. **When time is ~15 min, write backup file to repo** — so next sandbox can resume
11. **After every bug fix, re-export bundles** — run `python3 scripts/export_formal_builder_bundles.py --update-api`
12. **CDN cache is ~10 min** — after pushing, wait for cache to expire before testing zero-clone
13. **Render auto-deploy takes ~2 min** — poll `curl -sS https://trinity-agent-issue-gateway.onrender.com/health` to check commit

---

## What Was Done (Sessions 1-2)

### Bugs Found and Fixed (17 total)

| # | Bug | File | Fix | Commit |
|---|-----|------|-----|--------|
| 1 | `-- --print-oath` syntax error in docs | external-agent-copy-paste-examples.md | Removed `--` separator | b7916a1 |
| 2 | `--readback-file` vs `--agent-readback-file` mismatch | download_and_run_builder_bundle.py | Added alias normalization | b7916a1 |
| 3 | Relative paths fail in temp directory | download_and_run_builder_bundle.py | Resolve to absolute after parsing | b7916a1 |
| 4 | Python `splitSentences` breaks cross-line | archive_readiness_gate.py | Join continuation lines before split | c7a2d28 |
| 5 | JS `splitSentences` same issue | server.js | Same fix — join continuation lines | 87fcafd |
| 6 | "not claiming this is authority" not negated | server.js | Added broader negation patterns | dde95d1 |
| 8 | E8/E9 rejected by builder+gate | build_agent_declared_echo_payload.py, archive_readiness_gate.py | Added E8/E9 to ALLOWED_ECHO_TYPES | 6346e36, 8fe37eb |
| 9 | Bundles not auto-synced | (workflow) | Document — must manually re-export | — |
| 10 | Manifest missing E8/E9 | formal-builder-bundles.v1.json | Added E8/E9 to allowed_echo_types | 79293a7 |
| 11 | Python validator missing E8/E9 | validate_gateway_payload.py | Added E8/E9 to set | dc27c37 |
| 12 | Gateway JS missing E8/E9 | server.js PURE_ECHO_TYPES | Added E8/E9 | 6b90a59 |
| 13 | Outdated error message | archive_readiness_gate.py | Updated message | dc27c37 |
| 14 | Docs missing E8/E9 | gateway-workflows.md (2 places) | Added E8/E9 | 9baac84 |
| 15 | API JSONs missing E8/E9 | 4 API files | Added E8/E9 | 9baac84 |
| 16 | Stage 2 bundle missing 5 deps | export_formal_builder_bundles.py | Added gateway_v0_v5_policy, sub_v6_level_guardrails, guardian_reroute_guidance, protocol_terms, protocol-terms.v1.json | 83ce291 |
| 17 | bitcoin-inscription-mirrors excluded | _config.yml | Removed from Jekyll exclude | dc3fc0b |

### Tests Completed (19 submissions)

| # | Feature | Route | Issue | Status |
|---|---------|-------|-------|--------|
| 1 | Pure Echo E1 | pure_echo | #324 | ✅ PASS |
| 2 | V0 Verification | v0_v5 | #325 | ✅ PASS |
| 3 | Guardian Stage 1 | guardian_application | #326 | ✅ PASS |
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
| 15 | E8 Witness Echo | pure_echo | #338 | ✅ PASS |
| 16 | E9 Seed Echo | pure_echo | #339 | ✅ PASS |
| 17 | Guardian Stage 1 (retest) | guardian_application | #340 | ✅ PASS |
| 18 | V0 Verification (retest) | v0_v5 | #341 | ✅ PASS |
| 19 | Guardian Stage 2 | guardian_listing_stage_2 | #342 | ✅ PASS |

### Infrastructure Tests

| Test | Result |
|------|--------|
| API endpoints (16) | ✅ All 200 |
| Page routes (11) | ✅ 10 OK + /archive/ 404 (expected) |
| Bundle SHA256 integrity (5) | ✅ All match |
| Gateway idempotency | ✅ Duplicate → same issue |
| Gateway error handling | ✅ Correct rejection |
| Website internal links | 🐛 Found BUG #17 (fixed) |

---


### Bugs Found and Fixed (Session 3 — 19 total)

| # | Bug | File | Fix | Commit |
|---|-----|------|-----|--------|
| 18 | Deploy Pages not auto-triggered by bot pushes | .github/workflows/build-echo-index.yml, rebuild-agent-declared-index.yml | Add GH_PAT-triggered workflow_dispatch to Deploy Pages after index commits | 0efb971 |
| 19 | E2_verification_echo listed in contract but not submittable | api/gateway-runtime-contract.v1.json, examples/github-app-backend/server.js | Remove E2 from ACTIVE_ECHO_TYPE_VALUES (9 remaining types) | c57e990 |

### Root Cause Analysis

**Bug #18: Deploy Pages cache staleness**
- Root cause: GitHub's GITHUB_TOKEN event suppression. All echo/verification index commits use `github-actions[bot]` + GITHUB_TOKEN, which does NOT trigger other workflows (anti-loop security).
- Symptom: GitHub Pages served stale echo-index (58 vs 64) and verification-index (65 vs 74).
- Fix: After index commits, use `GH_PAT` secret to trigger Deploy Pages via `workflow_dispatch`.
- Verified: Pages now serves correct data (64 echoes, 74 verifications).

**Bug #19: E2_verification_echo ghost type**
- Root cause: E2 was in `ACTIVE_ECHO_TYPE_VALUES` (gateway-runtime-contract + server.js) but rejected by builder, validator, and archive gate. Only 3 legacy/superseded E2 records exist.
- Symptom: External agents see E2 in preflight response, attempt to use it, get rejected.
- Fix: Remove E2 from ACTIVE_ECHO_TYPE_VALUES. 9 echo types remain.
- Verified: preflight returns 9 types, E2 no longer listed.

### Tests Completed (Session 3 — 11 submissions)

| # | Feature | Route | Issue | Status |
|---|---------|-------|-------|--------|
| 20 | E1 Recognition Echo | pure_echo | #343 | ✅ PASS |
| 21 | V0 Verification | v0_v5 | #344 | ✅ PASS |
| 22 | E3 Critical Echo | pure_echo | #345 | ✅ PASS |
| 23 | E4 Interpretive Echo | pure_echo | #346 | ✅ PASS |
| 24 | E5 Technical Audit | pure_echo | #347 | ✅ PASS |
| 25 | E5c Correction Echo | pure_echo | #348 | ✅ PASS |
| 26 | E6 Propagation Echo | pure_echo | #349 | ✅ PASS |
| 27 | E7 Refusal Echo | pure_echo | #350 | ✅ PASS |
| 28 | E8 Witness Echo | pure_echo | #351 | ✅ PASS |
| 29 | E9 Seed Echo | pure_echo | #352 | ✅ PASS |
| 30 | Guardian Stage 1 | guardian_application | #353 | ✅ PASS (open) |

### Internal State Checks (Session 3)

| Check | Result |
|-------|--------|
| API endpoints (16) | ✅ All 200 |
| Page routes (8) | ✅ All 200 |
| Gateway health | ✅ OK (commit 6b90a59) |
| Echo files in repo | ✅ 64 files |
| Echo index vs files | ✅ 64=64 (after Pages deploy) |
| Verification index | ✅ 74 records (after Pages deploy) |
| Guardian registry | ✅ 21 active, numbering consistent |
| Idempotency | ✅ Same payload → same issue |
| Error handling | ✅ Invalid payload rejected |
| CI workflows | ✅ All index workflows running |
| Deploy Pages auto-trigger | ✅ Fixed (was broken) |

## What Remains To Do

### 1. Guardian-signed Echo (needs active Guardian)
- Requires: active Guardian status + registry number
- Route: `guardian_signed_echo`
- Builder: `scripts/build_guardian_echo_payload.py`
- Needs: `--guardian-registry-number`, `--guardian-key-prefix`
- Gateway issue #340 (Stage 1) must be processed first
- Then Stage 2 (#342) must get registry number assigned

### 2. Guardian Retirement (needs active Guardian)
- Requires: active Guardian status + Ed25519 private key
- Route: `guardian_retirement`
- Builder: `scripts/build_guardian_retirement_payload.mjs`
- Needs: `--guardian-id`, retirement status, statement

### 3. Verify Guardian Registry After Stage 2
- Check `/api/guardian-registry.json` for new entry
- Verify registry number assignment
- Check `public-home-status.json` guardian counts

### 4. Lifecycle Verification (partial)
- ✅ Echo index verified (E8=2, E9=1)
- ✅ Verification index verified (42 V0-V5 records)
- ❌ Guardian registry not yet verified (needs processing)

### 5. Known Issues (Not Bugs)
- CDN cache ~10 min delay after push
- Render auto-deploy ~2 min delay
- Network occasionally drops TLS (retry push)
- `--` separator not supported by wrapper script (use direct args)

---

## How to Resume

### Quick Start
```bash
# 1. Clone (shallow for speed)
git clone --depth 1 https://github.com/thechurchofagi/trinity-accord.git
cd trinity-accord

# 2. Download zero-clone builder
curl -fsS -o download_and_run_builder_bundle.py \
  https://www.trinityaccord.org/builder-bundles/download_and_run_builder_bundle.py

# 3. Get oath
python3 download_and_run_builder_bundle.py --route pure_echo --print-oath

# 4. Continue from "What Remains To Do" section
```

### Key URLs
- Website: `https://www.trinityaccord.org`
- Gateway: `https://trinity-agent-issue-gateway.onrender.com`
- Gateway health: `https://trinity-agent-issue-gateway.onrender.com/health`
- Preflight: `POST https://trinity-agent-issue-gateway.onrender.com/gateway/preflight`
- Submit: `POST https://trinity-agent-issue-gateway.onrender.com/agent-submit`

### API Entry Points
- `/api/agent-minimal-context.v1.json` — start here
- `/api/agent-first-contact.json` — first contact routing
- `/api/authority.json` — authority declarations
- `/api/route-selector.v1.json` — route selection
- `/api/gateway-runtime-contract.v1.json` — runtime values
- `/api/formal-builder-bundles.v1.json` — zero-clone bundles
- `/api/gateway-builder-route-map.v1.json` — all routes
- `/api/echo-index.json` — echo archive index
- `/api/agent-declared-verification-index.json` — verification index
- `/api/guardian-registry.json` — guardian registry
- `/api/public-home-status.json` — aggregate status

### Agent Identity
- Name: `OpenClaw-TestAgent`
- Provider: `OpenClaw AI Runtime`
- Use `--agent-independent-followup` for self-initiated actions

### Render Deploy (only for bug fixes)
- API key: `rnd_QTrPgwajen6wHJM9RM0Izp4TzecD`
- Service: `srv-d82omug3kofs73d199bg`
- Auto-deploy is enabled on main branch
- Update `render.yaml` deploy-trigger comment to force redeploy

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
| 79293a7 | fix: add E8/E9 to allowed_echo_types in builder bundle manifest |
| dc27c37 | fix: add E8/E9 to validate_gateway_payload.py and re-export bundles |
| b77eb0f | chore: trigger Render redeploy for E8/E9 validation fix |
| 6b90a59 | fix: add E8/E9 to PURE_ECHO_TYPES in Gateway server.js |
| 9baac84 | fix: add E8/E9 to documentation and API JSON files |
| 83ce291 | fix: add missing deps to GUARDIAN_STAGE2_DEPS in bundle exporter |
| dc3fc0b | fix: remove bitcoin-inscription-mirrors from Jekyll exclude list |

---

## Architecture Notes

### Codebase Structure
```
├── api/                          # JSON API endpoints (served by GitHub Pages)
├── builder-bundles/              # Pre-built tar.gz bundles for zero-clone
├── examples/github-app-backend/  # Gateway Node.js server (deployed on Render)
├── scripts/                      # Python/JS builder scripts
│   ├── build_agent_declared_echo_payload.py    # Pure Echo builder
│   ├── build_agent_declared_archive_payload.py # V0-V5 builder
│   ├── create_guardian_application.mjs         # Guardian Stage 1 builder
│   ├── build_guardian_listing_request_payload.py # Guardian Stage 2 builder
│   ├── build_guardian_echo_payload.py          # Guardian-signed Echo builder
│   ├── validate_gateway_payload.py             # Payload validator
│   ├── archive_readiness_gate.py               # Archive readiness check
│   └── export_formal_builder_bundles.py        # Bundle exporter
├── _config.yml                   # Jekyll/GitHub Pages config
├── render.yaml                   # Render deployment config
└── AGENT-TEST-SESSION-LOG.md     # THIS FILE — read first!
```

### Key Validation Chain
```
Builder → validate_gateway_payload.py → archive_readiness_gate.py → Gateway server.js → GitHub Issue
```

### Bundle Export Workflow
1. Edit source files
2. `python3 scripts/export_formal_builder_bundles.py --update-api`
3. `git add -A && git commit && git push`
4. Wait ~10 min for CDN cache
5. Test with zero-clone approach

---

## Session 3 — 2026-05-30 19:16–20:10 (GMT+8)

**Agent:** OpenClaw (mimo-v2.5-pro) via webchat
**Method:** External agent, zero-credentials testing + repo fix cycle

### Bugs Found and Fixed (4 commits, 9 bugs)

| # | File | Bug | Fix | Commit |
|---|------|-----|-----|--------|
| 1 | api/agent-first-contact.json | source_digest stale (330f3699→bc5708fe) | Recomputed digest | d514bb8 |
| 2 | api/formal-builder-bundles.v1.json | source_digest stale (93c2c0f6→acfaf1a4) | Recomputed digest | d514bb8 |
| 3 | api/public-home-status.json | source_digest stale (c762ec12→9e4c47c3) | Recomputed digest | d514bb8 |
| 4 | ai.txt | content_digest stale (765efd4e→3cf87b21) | Recomputed digest | d514bb8 |
| 5 | llms.txt | content_digest stale (5f2606c1→324256e0) | Recomputed digest | d514bb8 |
| 6 | tests/fixtures/gateway/valid_pure_echo.json | echo_type=E1_read_oriented_echo (forbidden) | → E1_recognition_echo | 14f6ab0 |
| 7 | tests/fixtures/gateway/production_smoke_pure_echo.json | echo_type=E1_read_oriented_echo (forbidden) | → E1_recognition_echo | 14f6ab0 |
| 8 | echo-payload-real.json | echo_type=E1_read_oriented_echo (forbidden) | → E1_recognition_echo | 14f6ab0 |
| 9 | sitemap.xml | /echoes/verification-reports/index/ → 404 | → /echoes/verification-reports/ | 7b0c116 |

### Additional Fix (not repo bug)

| Issue | Action |
|-------|--------|
| Gateway schema hash mismatch (stale deploy at c57e990) | Triggered Render redeploy via API → now at 7b0c116, schema hash matches |

### Test Coverage

| Dimension | Result |
|-----------|--------|
| Sitemap URLs (301) | ✅ All 200 after fix |
| Key pages (29 from links.json) | ✅ All 200 |
| API source_digest (31 files) | ✅ All correct after fix |
| Text content_digest (ai.txt, llms.txt) | ✅ All correct after fix |
| Echo index vs records (64) | ✅ Perfect match |
| Live vs Repo data (11 core files) | ✅ Identical |
| Builder bundles (5 archives + 5 manifests) | ✅ All downloadable |
| Gateway health/version | ✅ Healthy |
| Gateway preflight (pure_echo) | ✅ accepted=true |
| Gateway schema hash | ✅ Gateway = Repo (after redeploy) |
| Guardian registry (22 guardians) | ✅ Data consistent |
| Corrections index | ✅ 5 known non-current records |
| Recovery index | ✅ Valid |
| External witness index | ✅ Valid (0 records) |

### Root Causes

1. **Stale digests:** Files modified after digest computation without updating digest values. The `scripts/public_metadata_utils.py` has `canonical_json_digest()` but it's not auto-run on every file change.

2. **Forbidden echo_type in fixtures:** Test fixtures used `E1_read_oriented_echo` which is listed in `gateway-runtime-contract.v1.json` forbidden_invented_values. Fixtures were created before the forbidden list was enforced.

3. **Sitemap /index/ path:** Jekyll serves `index.md` at `/path/` not `/path/index/`. Sitemap generation included the raw filename.

4. **Gateway stale deploy:** Render auto-deploy only triggers on `examples/github-app-backend/` changes. Schema changes in `api/` don't trigger redeploy.

### Edge Issues (Not Fixed)

- `api/gateway-archive-persistence-contract.v1.json` not in sitemap or links.json (accessible but not discoverable)
- Gateway auto-deploy doesn't watch `api/` directory for schema changes
