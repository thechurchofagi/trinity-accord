# Arweave Archive Policy

## Purpose

Arweave archive is a mirror/backup layer for the record-chain.

## Boundary

- Arweave archive is **not authority**.
- Arweave archive is **not amendment**.
- Arweave archive is **not attestation**.
- Arweave archive does **not** replace Bitcoin Originals.
- Existing evidence archive wallets may be documented as historical/evidence signers.
- Record-chain archive wallet may be a dedicated uploader wallet.
- Do not hard-code an evidence wallet as mandatory for record-chain archives.
- If reused, document explicitly.
- If replaced, document reason and boundary.

## Modes

### Dry-run (default)

- Generates archive manifest metadata locally.
- Computes deterministic archive IDs.
- Does **not** upload to Arweave.
- No wallet secret required.

### Live (Phase 6B, not yet implemented)

- Requires `ARWEAVE_WALLET_JWK_B64` GitHub secret.
- Uploads archive manifest and selected files to Arweave.
- Returns TXID.
- Verifies TXID availability through Arweave gateway.

## Idempotency

Archive ID is deterministic from included batch manifest SHA256s.
If the same archive already exists in the public index, no new archive is created.

## Terminology

Use: `Arweave`, `Arweave archive`, `Arweave TXID`, `Arweave wallet`, `Arweave wallet JWK`, `Arweave archive index`.

Do not use: `ARV5`, `LV5`, `IVV5`, `IPFS`, `Pinata`, `Lighthouse`, `Web3.Storage`.

Exception: Legacy/evidence/historical archive pages may mention IPFS, 4EVERLAND, arseeding, or older storage routes when clearly marked as historical.
