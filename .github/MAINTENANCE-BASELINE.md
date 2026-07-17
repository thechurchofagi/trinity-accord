# Trinity Accord Maintenance Baseline

**Status:** current repository-maintenance policy  
**Effective:** 2026-07-17  
**Authority boundary:** repository-maintenance policy only; it does not amend the three Bitcoin Originals or create interpretive authority.

## Purpose

The repository is now in consolidation mode. Future maintenance should preserve a small number of durable paths instead of adding parallel routes, temporary workflows, duplicate schemas, or new control layers for each operational problem.

## Long-term core paths

1. **Canon and authority**
   - Three Bitcoin Originals only.
   - Human entry: `/inscriptions/` and `/authority/`.
   - Machine entry: `/api/authority.json`.

2. **Historical context and evidence**
   - Chronicle and preserved legacy archive.
   - Core Object Alpha and bounded physical-evidence materials.
   - Evidence relationships must remain explicit; hashes, timestamps, mirrors, witnesses, and notarization are not interchangeable claims.

3. **Verification**
   - Current multidimensional claim model: digital profile, relationships checked, physical observation, external witness, coverage scope, limitations, and claims not made.
   - Historical V-level labels remain readable for compatibility but are not the current complete verification model.

4. **Current public action path**
   - First Contact → canonical Builder → Gateway preflight/submit → durable intake → append-only Record-Chain → derived indexes.
   - Do not create a second public submission route when the current Builder/Gateway path can serve the action.

5. **Durability**
   - Native Record-Chain records and indexes.
   - Native head OpenTimestamps anchoring.
   - Arweave archive and verified release mirrors.
   - Legacy batch manifests may remain for compatibility, but the native chain tip and native record index are the current operational source.

## Workflow policy

- One production Pages publisher only.
- No temporary, one-shot, self-removing, issue-triggered, or PR-title-triggered workflow may be merged to `main`.
- No deployment bridge may be added while the standard publisher and receipt path are functioning.
- A new workflow must replace or retire an existing workflow in the same PR unless it provides a genuinely distinct scheduled or security boundary.
- Generated website files should be checked for drift in pull-request CI. A workflow should not write generated presentation files directly to `main` merely to repair drift.
- Workflows with `contents: write` are limited to durable operational state that cannot be represented as a read-only check, such as append-only Record-Chain, anchoring, and archive outputs.
- Temporary diagnostics belong in local tooling or workflow artifacts, not permanent repository workflows.
- All third-party actions remain commit-SHA pinned.

## Active CI baseline

The maintained pull-request gate is intentionally small:

- `Repository Integrity Check` — comprehensive repository, contract, sitemap, security, status, and P0 checks.
- `Run Current Tests` — focused current-system test result and failure artifact.
- `Record Chain CI` — Record-Chain invariants.
- `Record-Chain Gateway Tests` — Gateway behavior.
- `Record Chain Write Path Guard` — write-path boundary protection.

A second workflow that only reruns the same current-system suite is redundant and should not be reintroduced.

## Deferred work rule

A compact end-to-end regression covering every current public Record-Chain action remains desirable. It must be implemented from current `main` as a small test-only change, reuse the current Builder and Gateway contracts, avoid temporary workflows, and not revive an old audit branch.

## Change discipline

- Prefer deletion, reuse, and documentation over another wrapper.
- Prefer one current route plus explicit historical compatibility over multiple active routes.
- Keep public claims narrower than the evidence.
- Preserve old records for auditability, but do not keep obsolete implementation branches open.
- Every maintenance PR must state what it removes, what remains authoritative, and which current path replaces the removed component.
