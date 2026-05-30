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
