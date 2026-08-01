---
title: "Arweave Archive Policy"
permalink: /docs/arweave-archive-policy/
---

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

### Live (implemented)

- Requires `ARWEAVE_WALLET_JWK_B64` GitHub secret.
- Runs on the weekly Wednesday `07:17 UTC` continuity window, and pays only
  when a mature Native OTS proof and new Record-Chain data are available.
- The first Weekly Continuity archive is a self-contained `full_snapshot`;
  later versions are contiguous `incremental_delta` payloads.
- Uploads the deterministic payload, records its TXID, downloads the bytes
  again, and requires the readback SHA-256 to match before marking it archived.
- Enforces all of these non-bypassable limits: one paid upload of each class
  per UTC day, 8 MiB maximum payload, 0.05 AR maximum single reward, 0.50 AR
  maximum rolling 30-day spend, and at least 0.25 AR wallet reserve.
- Environment variables may make these limits stricter, but may not loosen
  the hard ceilings.

The public archive index currently records historical daily archives as well
as the newer weekly policy. Historical entries remain evidence of prior live
uploads; they do not re-enable daily paid uploads.

## Recovery access paths

An Arweave TXID and expected SHA-256 identify the payload. A gateway URL is
only an access path and is never treated as the identity of the archive.

Quarterly Weekly Continuity recovery attempts and cross-checks:

- `https://arweave.net/{txid}`;
- `https://arweave.net/raw/{txid}`;
- `https://ar-io.net/{txid}`;
- `https://g8way.io/{txid}`.

Successful gateways must return byte-identical content, and the consensus
bytes must equal the repository-preserved expected SHA-256. One operator or
one URL being unavailable therefore does not by itself make the archive
unrecoverable. A disagreement is a hard failure, not a majority vote.

## Idempotency

Archive ID is deterministic from included batch manifest SHA256s.
If the same archive already exists in the public index, no new archive is created.

## Terminology

Use: `Arweave`, `Arweave archive`, `Arweave TXID`, `Arweave wallet`, `Arweave wallet JWK`, `Arweave archive index`.

Do not use: `ARV5`, `LV5`, `IVV5`, `IPFS`, `Pinata`, `Lighthouse`, `Web3.Storage`.

Exception: Legacy/evidence/historical archive pages may mention IPFS, 4EVERLAND, arseeding, or older storage routes when clearly marked as historical.
