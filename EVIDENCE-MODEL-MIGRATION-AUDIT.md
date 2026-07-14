---
title: "Evidence Model Migration Audit"
permalink: /evidence-model-migration-audit/
---

# Evidence Model Migration Audit

> Non-amending repository migration audit. Bitcoin Originals remain final.

## Result

**Critical active entrypoint migration: complete.**

The initial automated scan examined 2,180 text/JSON/HTML files and produced 144 raw review candidates. Those candidates were then classified instead of being mechanically rewritten.

## Migrated active discovery and reading surfaces

- `README.md`, `/verify`, `/verification-materials`, `/agent-start`
- `/evidence-relationship-guide/`
- `.well-known/trinity-accord.json`
- `.well-known/agent.json`
- `api/links.json`
- `api/agent-minimal-context.v1.json`
- `api/agent-first-contact.json`
- `api/agent-start.v2.json`
- `api/agent-required-reading.json`
- `api/agent-task-router.v1.json`
- `api/verification-materials.json`
- `api/verification-quick-map.json`
- `/agent-first-contact`, `/agent-verify`, `/external-agent-quickstart`
- homepage and `llms-full.txt`

These surfaces now expose the preferred evidence relationship map, descriptive verification profiles, and action-based context profiles.

## Intentionally retained compatibility surfaces

The current Record-Chain Builder, Gateway, Render service, submission schema, field guidance, oath/readback flow, and archived record formats still use `V0–V5`, `CC`, and CRL fields. They remain required compatibility fields until a separately versioned runtime/schema migration is designed and deployed.

No Builder, Gateway application, Render configuration, submission schema, or runtime source file was changed by this migration.

## Intentionally frozen historical surfaces

Historical Echoes, verification reports, old submissions, audit snapshots, system-test captures, deprecated route archives, and prior examples retain the terminology that was true when they were created. Rewriting them would damage provenance.

## Specialized technical taxonomies

Component levels such as `B`, `D`, `C`, `N`, `P`, and `T`, plus legacy V profiles, remain available as detailed compatibility vocabulary. They no longer serve as the preferred headline model for new prose.

## Preferred model

1. Select the action from `/api/context-action-profiles.v1.json`.
2. Identify the evidence relationship through `/api/evidence-relationship-map.v1.json`.
3. Perform and report the exact operation.
4. Select the weakest supported descriptive profile from `/api/verification-profiles.v1.json`.
5. Report physical observation and external witness separately.
6. Supply legacy CC/V fields only where the current Builder or archived schema requires them.

## Validation performed before final commit

The migrated worktree passed:

- evidence relationship and legacy pointer mirror tests;
- the complete `p0-current` gate;
- the full current-system test suite;
- Builder receipt-boundary, oath/readback, help-link, public-route, and CLI-help checks;
- Render deploy-boundary checks;
- Gateway schema-parity, runtime-contract, and recovery-link checks;
- an explicit diff guard confirming that Builder runtime, Gateway application, Render configuration, submission schema, and field-guidance files were not modified.

A separate repository CI run is required after the permanent migration commit; bot-authored follow-up commits may appear as `action_required` with no jobs and are not treated as test results.

## Remaining critical migration gaps

None identified in active discovery, reading, verification navigation, Builder compatibility, or Render/Gateway boundaries.
