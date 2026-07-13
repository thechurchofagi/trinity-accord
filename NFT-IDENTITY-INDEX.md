# NFT Identity Index

`nft-identity-index.json` links each backed-up NFT to two different kinds of immutable identifiers:

1. **On-chain identity and mint evidence**
   - EIP-155 chain ID
   - token standard (`erc721` or `erc1155`)
   - contract address
   - token ID
   - mint transaction hash
   - block number and block hash
   - transaction index and log index
   - mint event type, recipient and quantity

2. **Content recovery references**
   - metadata and media Arweave transaction IDs
   - expected root CIDs
   - CAR SHA-256 digests and sizes

The canonical NFT identity is the chain, contract address and token ID together. A mint transaction hash is a direct evidence link, but it is not sufficient by itself because one transaction can mint multiple NFTs. The `log_index` (and `batch_index` for ERC-1155 batch events) identifies the exact mint event within that transaction.

## Storage boundary

This repository stores the structured identity index because it is small, reviewable and useful for direct lookup. Large CAR and media payloads remain in Arweave and GitHub Releases. The identity index does not duplicate binary NFT content.

## Regeneration

Set `ETH_RPC_URL` to an Ethereum-compatible JSON-RPC endpoint and run:

```bash
node scripts/generate_nft_identity_index.mjs
python3 scripts/test_nft_identity_index_contract.py
```

The generator scans zero-address ERC-721 and ERC-1155 transfer logs, selects the earliest mint event for every token in `token_index.json`, and re-verifies the selected event against its transaction receipt. It fails closed if any NFT cannot be resolved or any receipt does not contain the expected mint log.

The optional high-160-bit address and low-96-bit serial decomposition is only an informational interpretation of packed token IDs. It is not used as the canonical identity or as evidence of authorship.
