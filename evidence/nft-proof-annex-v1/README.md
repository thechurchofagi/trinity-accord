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

## L2 — compact execution inclusion

A full Ethereum transaction/receipt trie is reconstructed from the historical mint block during capture. The repository preserves only what is required for offline verification of each NFT mint:

- target raw signed transaction;
- target encoded receipt;
- Merkle-Patricia-Trie proof from the transaction to `transactionsRoot`;
- Merkle-Patricia-Trie proof from the receipt to `receiptsRoot`;
- execution block header fields required to recompute the block hash;
- the receipt-local log position used to cryptographically decode and verify the ERC-721 / ERC-1155 mint event.

This is cryptographically equivalent for target inclusion to preserving the full reconstructed tries, while avoiding repeated storage of unrelated transactions and receipts.

Ethereum receipt RLP does **not** encode the JSON-RPC `logIndex`. `logIndex` remains a historical lookup coordinate. During capture it is resolved to `receipt_log_position`; offline verification proves and decodes the actual receipt log at that position.

## L3 — consensus finality

L3 is deduplicated by execution block. Multiple NFT mints in one execution block share one L3 witness.

Each L3 witness follows the same model as `ethereum-evidence-annex-v1`:

1. the L2-verified execution block hash is SSZ-proven into the corresponding Beacon block body;
2. the Beacon header root is recomputed;
3. parent-root ancestry is verified to an explicitly named trusted finalized descendant Beacon root;
4. cross-provider canonical/finalized observations are retained as provenance only.

L3 therefore remains explicitly **checkpoint-relative under Ethereum weak subjectivity**. It is not claimed to be trust-free finality from no starting checkpoint, and it is not an absolute real-world clock attestation.

## Authority boundary

The three Bitcoin Originals remain the sole and final Canon. NFT evidence is non-amending historical chronicle/recovery evidence. This annex does not elevate NFT records into authority over the Accord.

## Verification

After proof material has been captured:

```bash
python3 scripts/build_nft_cryptographic_commitment.py --check
python3 evidence/nft-proof-annex-v1/verification/verify_nft_proof_annex.py
```

The verifier is fail-closed. It verifies the collection commitment, exact proof-file byte bindings, MPT transaction and receipt inclusion, the mint event itself, execution block header hash, SSZ execution-block inclusion, and checkpoint-relative Beacon ancestry.
