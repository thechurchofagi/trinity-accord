---
title: "Record-Chain Anchoring"
permalink: /docs/record-chain-anchoring/
---

# Record-Chain Anchoring

## Layer Architecture

### Record Hash Chain

Each native record contains:

- `content_sha256` — hash of record content excluding chain metadata
- `record_sha256` — hash of full record excluding record_sha256 itself
- `previous_record_sha256` — link to prior record

### Batch / Merkle Layer

Each batch manifest contains:

- `record_sha256_list` — ordered list of included record hashes
- `merkle_root_sha256` — Merkle root of the record hash list
- `previous_batch_manifest_sha256` — link to prior batch
- `batch_manifest_sha256` — hash of full manifest excluding batch_manifest_sha256

### OpenTimestamps (OTS) Layer

- Batch manifests are timestamped via OpenTimestamps.
- OTS proofs are **timestamp evidence only**.
- OTS is **not authority** or **attestation**.
- OTS proofs are stored as `.ots` files alongside batch manifests.

### Arweave Archive Layer

- Archive metadata mirrors chain/batch data.
- Dry-run first; live upload in Phase 6B.
- Arweave archive is **mirror only**, not authority.
- Archive IDs are deterministic from included batch range + source hash.

## Workflow Chain

```
Append Record Chain Entries (existing)
  → Record Chain Anchor (new)
    → Record Chain Arweave Archive (new)
```

## Status APIs

- `/api/record-chain-anchor-status.json` — OTS stamp status per batch
- `/api/record-chain-arweave-index.json` — Arweave archive index
- `/api/record-chain-status.json` — overall record-chain status

## Boundary

None of these layers amend or replace the Bitcoin Originals.
They only make later reception records easier to verify and harder to alter silently.
