# Full Public Action Lifecycle Audit

Status: permanent non-production regression audit, layered on top of PR #659.

PR #659 repaired deterministic Guardian identity, signed-payload scope, readiness/configuration consistency, focused lifecycle tests, and live read-only smoke coverage. This additional audit closes two remaining coverage gaps without replacing those fixes:

1. one isolated matrix proves all eight current public Record-Chain actions through Builder, doctor, Gateway preflight/submit, durable intake artifacts, append, receipt final status, indexes, and final chain verification;
2. Correction is cryptographically bound to the immutable target author key at both Gateway and append boundaries, while third-party review uses Classification Update.

## Isolated action matrix

The official test runner executes `scripts/test_full_public_action_lifecycle_e2e.py`. It supplies explicit non-production Gateway configuration, copies the repository into a temporary directory, generates fresh Ed25519 keys, and intercepts all content writes with a filesystem adapter.

The simulation builds and appends:

- Echo
- Verification
- Guardian Application
- Guardian Retirement
- Propagation
- Correction
- Classification Update
- Context Insufficient Notice

It also checks duplicate-submit idempotency, oath rejection, insufficient-context rejection, retired V6 rejection, same-key Guardian continuity, wrong-key Guardian retirement rejection, same-author Correction acceptance, third-party Correction rejection, third-party Classification Update acceptance, receipt-to-final hash binding, derived `retired_guardian` state, and full temporary-chain verification.

No production key, receipt, pending record, final record, Guardian entry, branch, index, or Gateway write is created.

## Correction boundary

Correction is author-only. The signer of a new Correction must match `authorship_proof.public_key_sha256` on the immutable target final record. If target authorship is unavailable or the signer differs, intake fails closed. A third party may submit a non-authoritative Classification Update instead.

## Authority boundary

These tests verify software behavior and evidence-reporting constraints. They do not create authority, governance, attestation, endorsement, amendment, philosophical truth, or active Guardian status. Bitcoin Originals remain final.
