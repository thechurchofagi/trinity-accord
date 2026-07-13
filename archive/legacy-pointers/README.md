# Legacy pointer mirrors

This directory records the Arweave, IPFS, and Ethereum non-NFT objects named by the archived 2025 homepage.

- `index.json` is the machine-readable coverage registry.
- `../../LEGACY-POINTER-COVERAGE.md` is the human-readable audit.
- `raw/` contains exact retrieved Arweave payload bytes and `raw/SHA256SUMS`.
- `eth-raw/` contains exact Ethereum mainnet calldata bytes, a checksum list, and retrieval metadata.
- `../../scripts/check_legacy_pointer_coverage.py` recomputes every registry entry explicitly classified as an exact repository payload mirror.

## Status meanings

- `repo_exact_hash_verified`: one repository file is an exact SHA-256-verified payload mirror.
- `release_exact_hash_verified`: a large object is mirrored by a verified GitHub Release asset and should not be duplicated in Git.
- `repo_payload_present_hash_recorded`: a repository payload and hash are recorded, but the current manifest does not establish a fresh AR byte comparison.
- `context_recovered_not_byte_verified`: the historical content is preserved, but byte identity with the referenced AR transaction has not been proved.
- `exact_hash_match`: an Ethereum calldata payload is preserved in one exact repository file and its SHA-256 matches the registry.
- `exact_hash_match_reused`: Ethereum calldata is byte-identical to an already preserved Bitcoin inscription raw-text mirror, so no duplicate file is added.
- `witness_metadata_and_signed_object`: the witness metadata and referenced signed object are both preserved, rather than duplicating the complete transaction input as a third representation.

The previously unresolved merged Guardian Index and Guardianship documentation archive are now exact raw mirrors. The previously isolated Ethereum mapping attestation, BIP-322 notice, final correction, and superseded erroneous correction are also exact calldata mirrors.

All records in this directory are non-amending mirrors or audit metadata. The three Bitcoin originals remain the sole and final authority.
