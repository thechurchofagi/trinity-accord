# SECURITY.md — Trinity Accord Security and Correction Policy

## Scope

This document covers the security policy for the Trinity Accord repository, including vulnerability reporting, correction and revocation procedures, and the non-deletion/tombstone policy that preserves the integrity of the public trust protocol.

## Reporting Contact

Security vulnerabilities and data integrity issues should be reported via GitHub Security Advisories or by opening a private issue with the `security` label. Do not disclose vulnerabilities publicly before they are triaged.

## Severity Levels

| Level | Description |
|-------|-------------|
| **Critical** | Compromise of trust-root keys, Bitcoin inscription integrity, or authority manifest. Immediate response required. |
| **High** | Incorrect attestation counts, missing revocation records, or corrections-index integrity failures. Response within 24 hours. |
| **Medium** | Schema validation bypasses, missing lifecycle metadata, or stale copy propagation issues. Response within 72 hours. |
| **Low** | Documentation gaps, non-critical metadata inconsistencies, or cosmetic issues. Response within 1 week. |

## Response Process

1. **Triage** — Assess severity and scope of the issue.
2. **Preserve** — Ensure no existing records are hard-deleted. All corrections use tombstone records.
3. **Update corrections-index** — Add correction, revocation, or supersession records to `api/corrections-index.json`.
4. **Regenerate digests** — Recompute `source_digest` for any modified index files.
5. **Run tests** — Execute all CI validators and lifecycle tests to confirm the fix.
6. **Publish notice** — Update affected public entrypoints and announce the correction.

## Non-Deletion / Tombstone Policy

**No public trust record may be hard-deleted.** We do not silently delete any record that was once public. When a record is corrected, revoked, superseded, or invalidated:

- The original record remains in place with lifecycle metadata added.
- A tombstone entry is added to `api/corrections-index.json`.
- The record's `is_current` is set to `false` and `historical_record_only` is set to `true`.
- The `counts_as_independent_attestation` field is set to `false` for revoked/superseded records.

This ensures full auditability and prevents silent revision of the public trust record.

## Stale Copy Notice

If any cached, quoted, or mirrored copy of this repository's data conflicts with the current `api/corrections-index.json`, the corrections index takes precedence. Always verify against the canonical source:

- Corrections index: `https://www.trinityaccord.org/api/corrections-index.json`
- Canonical repository: `https://github.com/thechurchofagi/trinity-accord`

## Boundary Statement

This security policy governs repository-maintained trust records. It does not amend the Bitcoin Originals. The Bitcoin inscriptions are canonical; all repository files are non-amending mirrors. Corrections and revocations apply only to repository-maintained indexes and metadata.
