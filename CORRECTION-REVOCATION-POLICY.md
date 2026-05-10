# CORRECTION-REVOCATION-POLICY.md — Trinity Accord Correction and Revocation Policy

## Purpose

This policy defines how corrections, revocations, supersessions, and invalidations are tracked in the Trinity Accord repository. It ensures that no public trust record is silently deleted and that all lifecycle transitions are explicit, auditable, and machine-readable.

## Key Distinctions

The following distinctions are critical for correct interpretation of repository records:

### 1. Historical Presence ≠ Current Validity
A record may exist in the repository's history without being currently valid. Check `is_current` and `historical_record_only` fields to determine current validity.

### 2. Archived ≠ Accepted
Archived records (including legacy records) are preserved for auditability. Archival does not imply acceptance, endorsement, or current validity.

### 3. Accepted Echo ≠ Independent Attestation
An accepted Echo record is explicitly not counted as independent attestation unless separately admitted through the formal independent attestation positive gate. The `do_not_count_as_attestation` flag preserves this boundary.

### 4. Superseded ≠ Deleted
A superseded record remains in the repository with `is_current=false` and `historical_record_only=true`. It is not removed; it is tombstoned in place.

### 5. Invalidated ≠ Hidden
An invalidated record remains visible and auditable. Invalidated records have `is_current=false` and `historical_record_only=true` but are never hidden or removed.

### 6. Revoked Trust Root ≠ Forgotten Trust Root
A revoked trust root remains in the historical roots list with explicit revocation metadata (`revoked_at`, `revocation_reason`). It is not removed from the trust-root-policy history.

### 7. Old Release Report ≠ Current Valid Report
A release report that has been superseded, revoked, or invalidated is no longer current. Check `report_status`, `is_current`, and `historical_report_only` fields.

### 8. Stale Cached llms/api ≠ Current State
Cached or mirrored copies of `llms.txt`, `ai.txt`, or API endpoints may become stale. When in doubt, check the corrections index at `api/corrections-index.json` for the current repository-maintained status.

## No-Hard-Delete Policy

**No public trust record may be hard-deleted.** This is a fundamental invariant of the Trinity Accord repository. We do not silently delete any record that was once public:

- Superseded records remain with lifecycle metadata.
- Revoked records remain with revocation metadata.
- Invalidated records remain with invalidation metadata.
- All lifecycle transitions are recorded in `api/corrections-index.json`.

Hard deletion would break the audit trail and undermine the public trust protocol's integrity. If a record must be removed from active use, it is marked as non-current with explicit reason — never silently erased.

## Corrections Index

The corrections index (`api/corrections-index.json`) is the authoritative source for:

- Current correction, revocation, and supersession records.
- Known non-current echo records.
- The no-hard-delete policy status.
- Limitations and boundary statements.

When any cached or quoted copy of repository data conflicts with the corrections index, the corrections index takes precedence.

## Bitcoin Originals Boundary

This correction and revocation policy applies only to repository-maintained records and metadata. It does not:

- Amend the Bitcoin Originals (inscriptions #97631551, #98369145, #98387475).
- Alter the canonical authority manifest or its signatures.
- Modify the BTC signature or ETH witness records.
- Override any on-chain anchoring or attestation.

The Bitcoin Originals are canonical. All repository files, including this policy, are non-amending mirrors.

## Lifecycle Status Values

### Record Lifecycle Status
| Status | is_current | historical_record_only | counts_as_independent_attestation |
|--------|-----------|----------------------|----------------------------------|
| `current` | `true` | `false` | (per record) |
| `accepted_current` | `true` | `false` | `true` |
| `superseded` | `false` | `true` | `false` |
| `revoked` | `false` | `true` | `false` |
| `invalidated` | `false` | `true` | `false` |
| `withdrawn` | `false` | `true` | `false` |
| `historical_only` | `false` | `true` | `false` |

### Report Status
| Status | is_current | historical_report_only |
|--------|-----------|----------------------|
| `current` | `true` | `false` |
| `historical` | `false` | `true` |
| `superseded` | `false` | `true` |
| `revoked` | `false` | `true` |
| `invalidated` | `false` | `true` |

---

## Release and Tag Immutability

Release tags must not be force-moved or deleted after publication. Release assets must not be silently replaced. If an asset must be replaced due to a verified integrity issue:

1. The old asset digest, replacement digest, reason, timestamp, and public notice must be recorded in `/api/corrections-index.json`.
2. The release must be marked as superseded or revoked in the corrections index.
3. The release verifier (`scripts/verify-release-assets.mjs`) must be re-run against the replacement.
4. A public notice must be published via the corrections index endpoint.

Protected tag rulesets enforce this policy at the GitHub control-plane level. See `CONTROL-PLANE-BASELINE.md` for current ruleset configuration.

### Tag Protection

Tags matching the following patterns are protected by GitHub ruleset:
- `v*`, `nft-*`, `release-*`, `evidence-*`, `archive-*`
- `core-object-*`, `signed-*`, `ots-*`, `flaw-*`
- `trinity-accord-*`, `redteam-*`

Protected operations: deletion, non-fast-forward updates.

### Release Asset Digest Chain

Every release asset set has a corresponding digest manifest. The verification chain is:
1. BTC signature covers authority manifest
2. Authority manifest declares digest-manifest pointers
3. Digest manifest covers file hash table
4. Release verifier checks assets against manifest
5. Corrections index can revoke/supersede any release report

## Recovery Procedures

Recovery procedures must check `api/corrections-index.json` before accepting recovered artifacts as current. See `RECOVERY.md` for the complete cold-start recovery guide.

## Claim Registry and Claim Corrections

If a public claim is found to overstate its evidence or limitations, correction should reference `api/claim-registry.json` and `api/corrections-index.json`. The claim registry provides machine-readable traceability for every core public claim, including its source files, evidence, validators, limitations, and corrections path.

Notarized evidence may record document existence, date, identity, signature, or other scope stated in the notarial act. It does not by itself constitute formal independent attestation of Trinity Accord claims. It must not increment formal independent attestation count unless separately admitted through the formal attestation positive gate.
