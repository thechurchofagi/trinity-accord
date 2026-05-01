# Trinity Accord OTS Proof Bundle — Arweave Mirror

## Purpose

This record preserves the Arweave upload and verification metadata for the Trinity Accord OTS proof bundle.

The bundle contains OpenTimestamps proof files, OTS backup files, verification reports, digest summaries, and process-context artifacts used to preserve the OTS verification record.

This Arweave upload strengthens long-term availability and independent retrievability of the OTS proof package.

## Boundary

This is an availability mirror only.

It does not amend, regenerate, reinterpret, or replace:

- Bitcoin Originals
- BTC signatures
- OTS Bitcoin anchoring
- digest-manifest records
- GitHub Release assets
- prior evidence-chain artifacts

It is not canonical authority.

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

The Arweave-downloaded payload was compared against the original local tar by SHA-256 and size.

Expected:

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
