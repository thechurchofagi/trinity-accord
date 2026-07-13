# Legacy pointer mirrors

This directory records the Arweave, IPFS, and Ethereum non-NFT objects named by the archived 2025 homepage.

- `index.json` is the machine-readable coverage registry.
- `../../LEGACY-POINTER-COVERAGE.md` is the human-readable audit.
- `../../scripts/check_legacy_pointer_coverage.py` verifies only entries explicitly classified as exact repository payload mirrors.

## Status meanings

- `repo_exact_hash_verified`: one repository file is an exact SHA-256-verified payload mirror.
- `release_exact_hash_verified`: a large object is mirrored by a verified GitHub Release asset and should not be duplicated in Git.
- `repo_payload_present_hash_recorded`: a repository payload and hash are recorded, but the current manifest does not establish a fresh AR byte comparison.
- `context_recovered_not_byte_verified`: the historical content is preserved, but byte identity with the referenced AR transaction has not been proved.
- `missing_raw_payload_metadata_preserved` / `documentation_pointer_only_no_raw_payload`: the pointer is preserved while raw retrieval remains unresolved.
- `metadata_only`, `content_embedded_not_isolated`, and `transaction_pointer_only` are not exact Ethereum payload mirrors.

All records in this directory are non-amending mirrors or audit metadata. The three Bitcoin originals remain the sole and final authority.
