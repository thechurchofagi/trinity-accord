# Trinity Accord Schema Lifecycle Policy

**Status:** current repository-maintenance policy  
**Effective:** 2026-07-17  
**Boundary:** this policy governs repository schemas and compatibility. It does not amend the Bitcoin Originals.

## Core rule

A published versioned schema is immutable by default. Do not silently change the meaning of an existing versioned schema to fit a new implementation.

When semantics must change:

1. create a new versioned schema or model;
2. identify what it supersedes;
3. update the current entrypoint documents and APIs;
4. preserve the old file for historical replay and audit;
5. add migration and compatibility tests where old records remain readable.

## Lifecycle states

### Current

A schema or model is current only when the active entrypoints point to it for new actions or new reports.

Currentness must be resolved from the maintained entrypoints, especially:

- `/api/agent-first-contact.json`
- `/api/agent-start.v2.json`
- `/api/record-chain-intake-gateway.v1.json`
- `/api/authority.json`
- `/api/verification-claim-model.v1.json`

File age, filename version, historical documentation, or the existence of a higher old V-level does not establish currentness.

### Compatibility

A compatibility schema remains available so historical records can be parsed, verified, migrated, or reproduced. It must not be presented as the preferred format for new submissions unless a current entrypoint explicitly says so.

Examples include:

- legacy Echo record shapes;
- retired aliases retained for archived records;
- V0–V5 Builder compatibility metadata when the multidimensional verification model carries the precise current claim;
- historical V4+/V6/V7/V8 labels, which remain historical-only and are forbidden for new verification submissions.

### Archived

An archived schema is retained only as historical evidence. It may be read, cited, or used to reproduce an old record, but it must not be accepted by a current public write path unless an explicit migration boundary says otherwise.

## Current contract families

The maintained contract families are:

- authority and Canon boundaries;
- Record-Chain submission and common-field contracts;
- current Echo record contract;
- multidimensional verification claim model;
- evidence-relationship model;
- context/readiness and agent-output policies;
- Builder bundle and Gateway intake contracts.

Do not create a parallel schema family for a problem already represented by one of these families. Extend through a new version only when the existing family cannot express the required semantics without ambiguity.

## Prohibited changes

- No in-place semantic rewrite of a published versioned schema.
- No new schema whose only purpose is to duplicate prose already exposed by the current field helper or entrypoint APIs.
- No new fixed verification ladder that recombines digital, physical, and witness claims into one inflated level.
- No reactivation of retired record types or aliases merely because historical files still contain them.
- No removal of historical schemas needed to verify existing signed or hashed records.
- No unversioned public write schema.

## Required change record

A PR that adds or changes a schema must state:

- lifecycle state: current, compatibility, or archived;
- exact predecessor or related contract;
- whether new submissions are affected;
- migration behavior for existing records;
- validation and regression tests;
- authority and non-amendment boundaries.

## Freeze declaration

All legacy schemas and historical verification labels present before this policy are frozen unless a current entrypoint explicitly designates them for new use. They remain available for audit and compatibility; they are not active merely because they remain in the repository.
