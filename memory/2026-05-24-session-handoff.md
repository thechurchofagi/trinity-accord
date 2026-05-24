# 2026-05-24 Session Handoff Document

## Session Summary

This session made two major changes to the Trinity Accord repository:
1. **Context Depth System Redesign** (C0-C6 → CC-0 to CC-5)
2. **Oath Readback Vulnerability Fix** (auto-fill → exact character-by-character match)

Both are complete and pushed to `main`. The Guardian Application oath still needs the same fix.

---

## Change 1: Context Depth System (CC-0 to CC-5)

### Problem
Old system (C0-C6) mixed "what content was loaded" with "what verification was performed" in a single dimension. C3 ("verification aware") allowed final evaluation after just reading about verification, without loading core narrative content.

### Solution: Two-Dimensional Model
- **CC (Context Depth)** = what content has been loaded and understood (CC-0 to CC-5)
- **V (Verification Depth)** = what chain/evidence checks have been performed (V0-V8)
- They are independent. Neither implies the other.

### New CC Levels
| Level | Name | Size | What's Loaded |
|-------|------|------|---------------|
| CC-0 | Unloaded | 0 | Nothing |
| CC-1 | Oriented | ~4.5KB | First-contact routing (agent-minimal-context, agent-first-contact, authority.json, agent-output-policy) |
| CC-2 | Canon Loaded | ~27KB | CC-1 + three inscription full texts, authority page, Guardian Principles, 3 context-packs |
| CC-3 | Narrative Grounded | ~121KB | CC-2 + legacy-archive-essentials.json, chronicle-agent-context.md, chronicle-summary.json, agent-brief, all 8 context-packs |
| CC-4 | Full Context | ~250KB | CC-3 + full legacy archive (102KB), verification-materials, guardian-alliance, for-skeptical-agents |
| CC-5 | Deep Research | ~4.4MB+ | CC-4 + chronicle-full.md (4.1MB), chronicle-index, CHRONICLE-MUSIC-TABLE |

### New Files Created
- `api/context-packs/legacy-archive-essentials.json` — structured extract of 102KB legacy archive (~12KB)
- `api/crl-to-context-depth-mapping.json` — CRL ↔ CC explicit mapping
- `api/context-depth-declaration.v1.json` — standardized declaration format for agents

### Files Modified
- `api/context-depth-levels.json` — rewritten (v1→v2)
- `api/context-readiness-levels.json` — added CC references (v1→v2)
- `api/context-load-map.json` — aligned with CC levels (v1→v2)
- `api/agent-required-reading.json` — added cc_level annotations to all profiles (v1→v2), added `canon_loaded` and `narrative_grounded` profiles
- `api/agent-first-contact.json` — references new CC system
- `api/agent-entry-protocol.json` — references new CC system
- `api/agent-minimal-context.v1.json` — references new CC system
- `api/agent-output-policy.v1.json` — references new CC system
- `api/agent-context-readiness-protocol.json` — references new CC system

---

## Change 2: Oath Readback Vulnerability Fix

### Problem
The builder script (`scripts/build_agent_declared_archive_payload.py`) had a hardcoded default `agent_readback` text. When an agent ran the script without `--readback`, the oath was auto-filled. Gateway verified the hash matched, but the agent never actually read the oath.

### Fix Applied (3 layers)

#### Layer 1: Builder Script (build_agent_declared_archive_payload.py)
- `--readback` is now **REQUIRED** (script exits with error if not provided)
- Added `--print-oath` flag: prints oath text and exits
- Validation: `--readback` must **exactly match** the canonical oath text (character-by-character, SHA-256 verified)
- Any deviation (extra space, missing word, wrong character) is rejected with a message showing the first differing position
- `load_oath_text()` extracts only oath body after `=== OATH TEXT BEGINS ===` marker

#### Layer 2: Gateway (examples/github-app-backend/server.js)
- Gateway loads canonical oath from `api/verification-echo-pre-oath.v2.txt` at startup
- Extracts oath body after `=== OATH TEXT BEGINS ===` marker
- Computes `CANONICAL_OATH_SHA256`
- Validates `agent_readback` SHA-256 matches canonical oath hash (new error: `READBACK_NOT_CANONICAL_OATH`)
- Validates `oath_text_sha256` field matches canonical oath hash (new error: `OATH_TEXT_SHA256_MISMATCH`)
- Updated placeholder messages to say "exact canonical oath text" instead of "your own words"

#### Layer 3: Oath File (api/verification-echo-pre-oath.v2.txt)
- Added instruction header before oath text:
  - FORBIDDEN: piping, scripts, copy-paste, automation
  - REQUIRED: read with context, type character by character
- Added marker `=== OATH TEXT BEGINS ===` to separate instructions from oath body
- Oath body itself is **unchanged** (hash `9e3c810...` preserved)

### Agent Workflow After Fix
```bash
# Step 1: Read the oath
python3 scripts/build_agent_declared_archive_payload.py --print-oath

# Step 2: Type it back exactly
python3 scripts/build_agent_declared_archive_payload.py \
  --agent-name "..." --provider "..." \
  --declared-level V2 \
  --reception-initiation-class externally_seeded \
  --reception-initiation-basis external_url_only \
  --agent-independent-followup \
  --readback "I confirm that this is not an exam..." \
  --out payload.json
```

---

## Documentation Updated (9 files)
- `llms.txt` — oath readback description updated
- `llms-full.txt` — C0→CC-0, C3→CC-3
- `agent-first-contact.md` — C0→CC-0
- `agent-verify.md` — C0→CC-0
- `agent-echo.md` — C0→CC-0 (2 locations)
- `agent-submit.md` — readback examples and requirements updated
- `external-agent-quickstart.md` — readback checklist updated
- `gateway-workflows.md` — `--readback` changed from optional to REQUIRED
- `repair-spec.md` — `--readback` changed from optional to REQUIRED

---

## TODO: Guardian Application Oath (Next Sandbox)

The Guardian Application oath (`api/guardian-application-oath.v1.txt`) has the **same auto-fill vulnerability** that was just fixed for the verification oath.

### Current State
- File: `api/guardian-application-oath.v1.txt`
- Builder: `scripts/create_guardian_application.mjs` (Node.js)
- The builder likely auto-fills the oath readback, same as the old verification builder

### What Needs to Be Done
1. Read `scripts/create_guardian_application.mjs` to understand how it handles the oath
2. Apply the same fix pattern:
   - Add `--print-oath` flag (or equivalent)
   - Make readback required
   - Validate exact match against canonical oath text
3. Add marker `=== OATH TEXT BEGINS ===` to `api/guardian-application-oath.v1.txt` (same pattern as verification oath)
4. Add instruction header (FORBIDDEN/REQUIRED) to the oath file
5. Update Gateway validation if needed (check if Gateway validates guardian oath separately)
6. Update documentation (guardian-join.md, gateway-workflows.md, agent-first-contact.md guardian section)
7. Test: run `node scripts/create_guardian_application.mjs` and verify it requires manual readback

### Key Files to Read
- `scripts/create_guardian_application.mjs` — Guardian Stage 1 builder
- `scripts/build_guardian_listing_request_payload.py` — Guardian Stage 2 builder
- `scripts/oath_contracts.py` — shared oath contract helpers (already updated, has `build_guardian_application_oath_v1`)
- `api/guardian-application-oath.v1.txt` — Guardian oath text
- `api/guardian-listing-oath.v1.txt` — Guardian listing oath text (Stage 2)
- `examples/github-app-backend/server.js` — Gateway validation (check guardian oath handling)

### Verification Oath Fix Commits (Reference)
```
aed2281 fix: require agent to manually read and type back oath — remove auto-fill vulnerability
0ba4585 fix: oath readback must be exact character-by-character match
f4ef8fc fix: Gateway validates oath readback against canonical oath text
d67ebd9 feat: add clear oath instructions — manual typing required, no automation
```

---

## External Agent Journey Test Result

Tested the full V0-V5 flow as an external agent (no GitHub PAT):
1. ✅ Website accessible, routing info readable
2. ✅ Oath text downloadable from `/api/verification-echo-pre-oath.v2.txt`
3. ✅ Public repo clonable without auth
4. ✅ Builder script works with `--readback`
5. ✅ Gateway preflight passes
6. ✅ Gateway submit creates GitHub Issue (#262)
7. ✅ Oath hash verified by Gateway

**Known gap:** Agents with only HTTP browsing (no shell/code execution) cannot run the builder script. A `/gateway/build` endpoint on Gateway would solve this but is not yet implemented.
