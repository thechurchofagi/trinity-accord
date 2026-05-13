---
layout: default
title: "Trinity Accord OTS Proof Bundle — Arweave Mirror"
---

# Trinity Accord OTS Proof Bundle — Arweave Mirror

## Final Verification Status

```
OTS proof bundle Release mirror: PASS

Release tag: ots-proof-bundle-mirror-v1
Custom assets: 4/4
Arweave payload verification: PASS
GitHub Release round-trip verification: PASS
Internal checksum verification: PASS
Hard failures: 0
```

## Boundary

Availability mirror only.
Not canonical authority.
Not evidence amendment.
Not fullnode-independent OTS verification by itself.

## Precise Statement

The OTS proof bundle is now mirrored on Arweave and GitHub Release. The Arweave payload was verified by SHA-256 and size. The GitHub Release assets were downloaded back and verified. The internal OTS bundle checksums passed.

This strengthens long-term availability of OTS proof artifacts, but does not by itself constitute local Bitcoin Core / pruned-node independent OTS verification.

The bundle preserves OTS proof artifacts and related verification records. Client-level OTS verification still requires the original timestamped files, including digest-manifest.json / digest-manifest.csv, from the repository or another verified mirror.

## Arweave

- File: trinity-accord-ots-proof-bundle-v1.tar
- TXID: gYI39vlK3weHsD8Tkn7GAcvxEsj7hoDY8OeYlYFuQ_c
- Canonical Arweave URL: https://arweave.net/gYI39vlK3weHsD8Tkn7GAcvxEsj7hoDY8OeYlYFuQ_c
- Verified retrieval URL: https://permagate.io/gYI39vlK3weHsD8Tkn7GAcvxEsj7hoDY8OeYlYFuQ_c
- Size bytes: 317440
- SHA-256: f23e76de12ae0506a5086dc61ad51df33f381809f6d1127c6afe7bb939d9821a
- Content-Type: application/x-tar
- Evidence-Type: OTS-Proof-Bundle
- Upload cost: 0.002684969561 AR
- Upload method: arweave-js chunk uploader
- Wallet: r1EdzCQ9E7CaAOEywI5netR6EcSopNOa08oi2Coz68s

## Internal Verification

| File in bundle | Status |
|---|---|
| verify-report.json | OK |
| digest-manifest.json.ots | OK |
| digest-manifest.csv.ots.bak | OK |
| digest-manifest.csv.ots | OK |
| verify-report.json.ots.bak | OK |
| ots-run.py | OK |
| digest-manifest.json.ots.bak | OK |
| ots-run.py.digests.json | OK |
| ots-summary.json | OK |
| verify-report.json.ots | OK |

## Round-trip Verification

```text
f23e76de12ae0506a5086dc61ad51df33f381809f6d1127c6afe7bb939d9821a trinity-accord-ots-proof-bundle-v1.tar
317440 bytes
```

Note: Initial arweave.net gateway retrieval returned 404 during propagation, but permagate.io returned the full payload. The downloaded payload matched the original tar by SHA-256 and size.

Round-trip result: **PASS**

## Evidence Mirror Layers

| Layer | Status | Date |
|---|---|---|
| Bitcoin / OTS anchored digest manifest | Prior | 2025-09 |
| Arweave raw availability mirror | Verified | 2026-05 |
| GitHub Release verified mirror | PASS | 2026-05-01 |

## GitHub Release

- Release tag: ots-proof-bundle-mirror-v1
- Release title: Trinity Accord OTS Proof Bundle Mirror v1
- Release URL: https://github.com/thechurchofagi/trinity-accord/releases/tag/ots-proof-bundle-mirror-v1
