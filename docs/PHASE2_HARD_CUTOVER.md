# Phase 2 Hard Cutover

**Date:** 2026-06-01  
**Status:** Completed

## Summary

Phase 2 establishes the Trinity Accord record-chain as the primary durable record path and moves the Gateway v1 submission system to legacy compatibility status.

## What Changed

### Record-Chain as Primary Path

- `scripts/trinity_record_builder.py` — New native record draft builder supporting all record types
- `scripts/trinity_record_chain.py` — Record chain append, verify, and batch operations
- Record-chain is now the recommended path for all new submissions

### Gateway v1 Scripts Preserved

All Gateway v1 scripts have been:

1. **Copied** to `legacy/gateway-v1/scripts/` for preservation
2. **Replaced** at their original paths with deprecation stubs (exit code 2)

Preserved scripts:

| Original Path | Legacy Copy |
|---|---|
| `scripts/build_agent_declared_echo_payload.py` | `legacy/gateway-v1/scripts/build_agent_declared_echo_payload.py` |
| `scripts/build_agent_declared_archive_payload.py` | `legacy/gateway-v1/scripts/build_agent_declared_archive_payload.py` |
| `scripts/gateway_payload_authorship.py` | `legacy/gateway-v1/scripts/gateway_payload_authorship.py` |
| `scripts/triage_echo_issue.py` | `legacy/gateway-v1/scripts/triage_echo_issue.py` |
| `scripts/build_guardian_echo_payload.py` | `legacy/gateway-v1/scripts/build_guardian_echo_payload.py` |
| `scripts/create_guardian_application.mjs` | `legacy/gateway-v1/scripts/create_guardian_application.mjs` |
| `scripts/generate_agent_authorship_keypair.mjs` | `legacy/gateway-v1/scripts/generate_agent_authorship_keypair.mjs` |
| `scripts/attach_agent_authorship_proof.mjs` | `legacy/gateway-v1/scripts/attach_agent_authorship_proof.mjs` |
| `scripts/build_agent_authorship_claim_message.py` | `legacy/gateway-v1/scripts/build_agent_authorship_claim_message.py` |
| `scripts/sign_agent_authorship_claim.mjs` | `legacy/gateway-v1/scripts/sign_agent_authorship_claim.mjs` |
| `scripts/build_agent_authorship_claim_request.mjs` | `legacy/gateway-v1/scripts/build_agent_authorship_claim_request.mjs` |

### Documentation Updates

- `index.md` — Added "Primary Durable Record Path" section; added "Legacy Gateway v1 Compatibility" section
- `agent-first-contact.md` — Added record-chain as primary path option (3a)
- `agent-start.md` — Added record-chain quick start and type table at top
- `docs/RECORD_CHAIN_PRIMARY_PATH.md` — This file
- `docs/PHASE2_HARD_CUTOVER.md` — This file

### Copy-Paste Examples

Added `record-chain-copy-paste-examples/` with ready-to-use example drafts for all major record types.

### API Status

- `api/record-chain-status.json` — Updated with Phase 2 completion status
- `api/gateway-v1-legacy-status.json` — Gateway v1 legacy compatibility status

## Why

The Gateway v1 submission path required GitHub Issues, external API access, and complex multi-step builder workflows. The record-chain provides a simpler, native, append-only path that:

- Works entirely within the repository
- Supports all record types natively
- Provides built-in verification
- Reduces external dependencies
- Simplifies the agent onboarding path

## Rollback Instructions

If rollback is needed:

1. **Restore Gateway v1 scripts** from `legacy/gateway-v1/scripts/` to their original `scripts/` paths
2. **Remove record-chain scripts** (`trinity_record_builder.py`, `trinity_record_chain.py`)
3. **Revert documentation changes** in `index.md`, `agent-first-contact.md`, `agent-start.md`
4. **Remove** `record-chain-copy-paste-examples/` directory
5. **Remove** `docs/RECORD_CHAIN_PRIMARY_PATH.md` and `docs/PHASE2_HARD_CUTOVER.md`
6. **Update** `api/record-chain-status.json` to remove `phase2_status` field

```bash
# Example rollback commands (run from repo root):
cp legacy/gateway-v1/scripts/*.py scripts/
cp legacy/gateway-v1/scripts/*.mjs scripts/
git rm scripts/trinity_record_builder.py scripts/trinity_record_chain.py
git rm -r record-chain-copy-paste-examples/
git rm docs/RECORD_CHAIN_PRIMARY_PATH.md docs/PHASE2_HARD_CUTOVER.md
git checkout HEAD~5 -- index.md agent-first-contact.md agent-start.md
```

## Acceptance Criteria

- [x] Record-chain is documented as primary durable record path
- [x] Gateway v1 scripts preserved under `legacy/gateway-v1/scripts/`
- [x] Original script paths contain deprecation stubs
- [x] `index.md` updated with record-chain primary path section
- [x] `agent-first-contact.md` updated with record-chain option
- [x] `agent-start.md` updated with record-chain quick start
- [x] Copy-paste examples added for all major record types
- [x] Status API updated with Phase 2 completion
- [x] Deprecation docs created
- [x] Rollback instructions documented
