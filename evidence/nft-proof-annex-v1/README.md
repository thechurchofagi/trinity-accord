# NFT Cryptographic Proof Annex v1

This annex strengthens the 175 NFT chronicle records without creating another copy of the NFT media or CAR payloads.

## What is already preserved elsewhere

`nft-identity-index.json` already binds every NFT to its EIP-155 chain, token standard, contract, token ID, mint transaction/log coordinates, and Arweave recovery references. The large metadata/media CAR payloads remain in Arweave and GitHub Releases. This annex does not duplicate those bytes.

## L1 — collection commitment

`NFT-COLLECTION-COMMITMENT.json` deterministically projects the evidence-critical fields of all 175 NFT records, sorts them by canonical identity, and commits them with an RFC6962-style domain-separated SHA-256 Merkle tree.

The root commits to:

- chain ID, standard, contract and token ID;
- mint transaction hash, block hash/number, transaction index, event coordinates and mint semantics;
- metadata/media root CIDs, Arweave transaction IDs, CAR SHA-256 digests and sizes.

Presentation URLs and the informational packed-token-ID interpretation are deliberately excluded.

The preserved v1 collection commitment contains 175 leaves and has Merkle root:

```text
097bb48d98ab7fc036aed97f5b5fcb1a65962d64d327081277255d1829212267
```

## L2 — compact execution inclusion

A full Ethereum transaction/receipt trie was reconstructed from each historical mint block during capture. The repository preserves only what is required for offline verification of each NFT mint:

- target raw signed transaction;
- target encoded receipt;
- Merkle-Patricia-Trie proof from the transaction to `transactionsRoot`;
- Merkle-Patricia-Trie proof from the receipt to `receiptsRoot`;
- execution block header fields required to recompute the block hash;
- the receipt-local log position used to cryptographically decode and verify the ERC-721 / ERC-1155 mint event.

This is cryptographically equivalent for target inclusion to preserving the full reconstructed tries, while avoiding repeated storage of unrelated transactions and receipts.

The offline verifier also fail-closes on cross-field drift between the L1 identity record, capture summary, signed transaction and proven receipt. In particular it checks:

- the execution block number against the committed mint block number;
- the signed EIP-155 transaction chain ID against the committed chain ID;
- the proven receipt status against the committed receipt status;
- the ERC-721 / ERC-1155 standard against the proven event family;
- capture-summary block / transaction / receipt-log coordinates against the actual compact witness;
- the historical JSON-RPC `logIndex` declaration against the identity index.

Ethereum receipt RLP does **not** encode the JSON-RPC global `logIndex`. Therefore `logIndex` remains a historical lookup coordinate, not an independently chain-proven field. During capture it was resolved to `receipt_log_position`; offline verification proves and decodes the actual receipt log at that position and separately fail-closes if the retained historical `logIndex` binding drifts.

The frozen v1 inventory contains 175 distinct mint transactions, and all 175 compact L2 witnesses must pass offline verification.

## Frozen Ethereum proof primitives

The NFT verifier no longer imports executable verification logic from the separately maintained `ethereum-evidence-annex-v1` verifier. It loads only the frozen module:

`evidence/ethereum-proof-primitives-v1/ethereum_proof_primitives_v1.py`

Its exact SHA-256 is bound by `PRIMITIVES-MANIFEST.json` and checked before the module is executed. The v1 change policy is immutable: changes require a new primitives version rather than silently changing the meaning of the frozen NFT verifier.

## L3 — checkpoint-relative consensus finality

L3 is deduplicated by execution block. Multiple NFT mints in one execution block would share one L3 witness. In this specific frozen v1 inventory, the 175 NFT mint transactions happen to occupy 175 distinct execution blocks, so the resulting proof set contains 175 L3 witnesses.

Each L3 witness follows the same explicit weak-subjectivity model as `ethereum-evidence-annex-v1`:

1. the L2-verified execution block hash is SSZ-proven into the corresponding Beacon block body;
2. the Beacon header root is recomputed;
3. parent-root ancestry is verified to an explicitly named trusted finalized descendant Beacon root;
4. cross-provider canonical/finalized observations are retained as provenance only.

The legacy v1 report field remains named `L3_CONSENSUS_FINALITY` for format compatibility, but its precise semantic scope is **checkpoint-relative finality under Ethereum weak subjectivity**. It is not claimed to be trust-free finality from no starting checkpoint, and it is not an absolute real-world clock attestation.

All 175 preserved L3 witnesses must pass the offline verifier.

## Authority boundary

The three Bitcoin Originals remain the sole and final Canon. NFT evidence is non-amending historical chronicle/recovery evidence. This annex does not elevate NFT records into authority over the Accord.

## Preserved proof material

The checked-in annex contains:

- `NFT-COLLECTION-COMMITMENT.json` — deterministic 175-leaf L1 commitment;
- `proof-material/L2/` — 175 compact mint-transaction/receipt inclusion witnesses;
- `proof-material/L3/` — 175 block-level Beacon consensus witnesses;
- `proof-material/CAPTURE-SUMMARY.json` — exact proof paths, sizes and SHA-256 bindings;
- `reports/OFFLINE-VERIFICATION.json` — deterministic offline verification report;
- frozen, digest-bound Ethereum proof primitives used by the NFT verifier.

Large NFT media/CAR payloads are intentionally not copied into this annex.

## Verification

Run:

```bash
python3 scripts/build_nft_cryptographic_commitment.py --check
python3 evidence/nft-proof-annex-v1/verification/verify_nft_proof_annex.py
```

The verifier is fail-closed. It verifies the collection commitment, exact proof-file byte bindings, MPT transaction and receipt inclusion, signed-transaction chain ID, mint-event semantics, cross-field identity bindings, execution block header hash, SSZ execution-block inclusion, and checkpoint-relative Beacon ancestry.

The required `Run Current Tests` workflow performs the same proof verification offline on every pull request and on `main`. The one-time network capture workflow used to materialize the proof set was removed after the proof bytes were committed, so routine verification does not depend on Ethereum RPC or Beacon APIs.
