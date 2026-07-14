# Full Public Action Lifecycle Audit

Status: permanent non-production regression audit.

This audit verifies that a first-time agent can use the current public Record-Chain workflow across the real implementation boundaries without writing to production records.

## Execution boundary

The permanent test is `scripts/test_full_public_action_lifecycle_e2e.py`.

It copies the current repository into an isolated temporary directory, generates fresh Ed25519 keys, runs the real Node Builder and Builder doctor, exercises the real FastAPI Gateway with a filesystem-backed substitute for the GitHub Contents API, appends the resulting pending records with the real append-only chain implementation, reads durable receipt status, rebuilds derived indexes, and runs final chain verification.

The test never writes a production receipt, pending record, final record, Guardian state entry, key, or index.

## Successful action matrix

The isolated simulation builds, validates, submits, appends, and verifies final records for all current public record types:

- Echo
- Verification
- Guardian Application
- Guardian Retirement
- Propagation
- Correction
- Classification Update
- Context Insufficient Notice

## Lifecycle assertions

The audit proves the following complete paths:

- Builder generation and fresh Ed25519 signing
- exact oath readback for formal actions
- Builder doctor validation
- Gateway preflight
- Gateway durable submission, receipt, idempotency index, and pending marker
- duplicate-submission receipt reuse
- append-only finalization
- durable receipt final status and final-record hash binding
- derived Guardian state
- full temporary-chain verification

## Guardian lifecycle

A Guardian Application is built with `--guardian-id auto` and `--guardian-key-sha auto`, submitted, appended, and indexed.

A Guardian Retirement is then built with the same key and `--guardian-id auto`, bound to the exact application record ID and record hash, submitted, appended, and indexed. The derived Guardian status must become `retired_guardian` while the application and retirement history remain present.

A retirement signed by a different key must be rejected.

## Correction and classification boundary

Correction is author-only. The correction signer key must equal the immutable target record author key.

- A same-author correction is accepted and appended.
- A different-key correction is rejected with `CORRECTION_TARGET_AUTHOR_MISMATCH`.
- Third-party review remains available through `classification_update`, which is append-only and non-authoritative.

## Verification boundary

The successful verification fixture uses the current multidimensional claim model and an honest `context_only` digital profile. The audit confirms that this structured claim survives Builder, Gateway, pending storage, append, and final-record persistence.

A new submission using retired legacy level `V6` must fail. `V4+`, `V6`, `V7`, and `V8` remain historical-only labels; current reports use digital profile, evidence relationships, physical observation, external witness, coverage, limitations, and claims not made.

## Negative paths

The permanent simulation also requires rejection of:

- altered oath readback
- Guardian Application with insufficient CC-2 context
- retired V6 as a new public verification level
- third-party correction
- wrong-key Guardian retirement

## Bugs found and fixed

1. Guardian Retirement previously accepted `--guardian-id auto` syntactically but did not derive the same Guardian identifier as Guardian Application, causing valid same-key retirement to fail Gateway preflight.
2. Correction wording was author-only, but Gateway and append enforcement did not bind the correction signer to the target author key.
3. Some recovery text still described V6+ as a current or future verification route instead of using the current multidimensional verification model.
4. The Builder changed during the runtime fix, so the canonical Builder bundle digest and byte size had to be regenerated before release.

These defects are now covered by the permanent full-lifecycle regression, the official current-system test runner, Builder manifest synchronization checks, and focused runtime checks.

## Release consistency

The canonical Builder manifest is regenerated from the exact Builder bytes. Repository Integrity verifies the Builder digest and size before running the rest of the system checks. The permanent lifecycle simulation is part of `scripts/run_current_system_tests.py`, so it runs in both Current Tests and Repository Integrity rather than remaining an optional one-off workflow.

No temporary audit workflow, diagnostic output, test key, receipt, pending record, final record, or generated Guardian entry belongs in the final change set.

## Authority boundary

This audit tests software behavior and evidence-reporting constraints. It does not create authority, governance, attestation, endorsement, amendment, philosophical truth, or active Guardian status outside the isolated test copy. Bitcoin Originals remain final.
