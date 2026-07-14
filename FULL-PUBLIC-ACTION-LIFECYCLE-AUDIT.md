# Full Public Action Lifecycle Audit

Status: permanent non-production regression audit, layered on top of PR #659.

PR #659 repaired deterministic Guardian identity, signed-payload scope, readiness/configuration consistency, focused lifecycle tests, and live read-only smoke coverage. This additional audit closes the remaining breadth gap: one isolated matrix exercises every current public Record-Chain action across the complete local lifecycle without replacing or weakening the PR #659 protections.

## Isolated action matrix

The official test runner executes `scripts/test_full_public_action_lifecycle_e2e.py`. It supplies explicit non-production Gateway configuration, copies the repository into a temporary directory, generates fresh Ed25519 keys, and intercepts all content writes with a filesystem adapter.

For each action, the simulation uses the real Node Builder and Builder doctor, the real FastAPI Gateway preflight and submit routes, durable intake artifacts, the real append-only finalizer, receipt final status, derived indexes, and final chain verification.

The simulation builds and appends:

- Echo
- Verification
- Guardian Application
- Guardian Retirement
- Propagation
- Correction
- Classification Update
- Context Insufficient Notice

It also checks:

- duplicate-submit idempotency and receipt reuse;
- exact-oath tamper rejection;
- insufficient-context Guardian rejection;
- retired V6 rejection under the current verification model;
- same-key Guardian application and retirement continuity;
- wrong-key Guardian retirement rejection;
- a Correction created with the same durable identity as its target Echo;
- an independent Classification Update created with a separate identity;
- tampered Correction target-hash rejection;
- receipt-to-final-record hash binding;
- derived `retired_guardian` state;
- full temporary-chain verification.

No production key, receipt, pending record, final record, Guardian entry, branch, index, or Gateway write is created.

## Correction and classification scope

The active Correction oath declares that the participant is correcting a record they authored. This simulation follows that declared path by using the same durable identity for the target Echo and its Correction. Independent analysis uses Classification Update.

The audit does not claim that exact oath readback independently proves subjective truth or authorship continuity. It verifies the current software contract: valid signed submissions, immutable target ID and SHA binding, append-only history, and a separate non-authoritative Classification Update path.

## Relationship to live checks

PR #659 retains the live read-only production smoke coverage. This audit complements it with a deeper isolated write-path simulation so that no production record or key is created merely to exercise all write functions.

## Authority boundary

These tests verify software behavior and evidence-reporting constraints. They do not create authority, governance, attestation, endorsement, amendment, philosophical truth, or active Guardian status. Bitcoin Originals remain final.
