---
layout: default
title: "NFT Backup Provenance"
description: "Provenance chain for NFT individual backups."
---

# NFT Individual Backup — Provenance Chain

> Generated: 2026-04-30
> Purpose: Document how each NFT's backup is cryptographically linked to the Bitcoin signature

## Chain of Trust

```
Bitcoin BIP-340 Signature (valid ✅)
│  Address: bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf
│  Signs: SHA-256 of authority.jcs.json
│  Signature: cfde2fe789195b55b1bc8026061828243a250837d7ab33ff7565f2d4b6d52385...
│
└──▶ authority.jcs.json (v1.0.0)
     │  sha256: 41f95905e50cc699a7e6a3fcb0bd8633cf36170d3ef41170cd373467f8528b33
     │  Contains: 3 BTC Originals, 5 BTC Ancillary, 7 ETH Attestations, 8 Arweave Documents
     │
     └──▶ Arweave Document: "Primary Verification Archive (public)"
          │  TxID: j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk
          │  SHA-256: ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263
          │  Size: 24,246,033 bytes (24MB)
          │  Content: public-covenant-archive.zip (8 photos + 2 videos of Core Object Alpha)
          │
          └──▶ (This archive contains the physical evidence photos/videos)

     └──▶ Arweave Document: "digest-manifest.json"
          │  TxID: X2IuLCIM4vLJSzgRMl_YEmxYSvPceMrAdug9a3i7p4o
          │  SHA-256: c045642fe5cfab5eb78af7b40e98b9699dfff9121690e07ec6acaa07a445d6e9
          │  Size: 685,537 bytes
          │  Content: 884-file manifest with 6 hash algorithms each
          │  Files: 675 IPFS CARs + 86 DNG raws + 28 flaw photos + 11 fingerprints + ...
          │
          └──▶ (This manifest catalogs ALL local backup files)

     └──▶ Arweave Document: "digest-manifest.csv"
          │  TxID: i02XhY7No6NLZDfEwFUU6nZoGaPu7K0f42LDNDNnZEo
          │  SHA-256: 121c5a1da38f733c3991f8d3f030f39a019501d43828f84c13ea93ac3873511b
          │  Size: 502,283 bytes
          │  Content: CSV version of above
          │
          └──▶ (Same manifest, CSV format)

     └──▶ Arweave Document: "OTS anchor"
          │  TxID: TTi9d8fqm9Cw4yRPkwX4gdlaRzBnjJID-LAs9Y3CS0M
          │  SHA-256: fa3f306ab30525677595d9f38808a87a8dd96260468285c8f8066661e853d907
          │  Size: 3,614 bytes
          │  Content: OpenTimestamps proof anchoring digest-manifest to Bitcoin blockchain
          │
          └──▶ (Timestamps the manifest hash into BTC block)

## NFT Backup Path (the key chain)

```
Bitcoin Signature → authority.jcs.json → (references Arweave docs)
                                              │
                                              ▼
                            recovery-package.bin (700KB)
                            Arweave TxID: O-Rk3kFxesPGhuYP4KHAZl54xR2urDRKcGaVqjVnB-Q
                            IPFS CID: QmYCosJg44CXkFxLsJPBxKvWAJaFAcLMddp37sk9Gdr4Vd
                            SHA-256: f8b0dad700ad7a88ba343930ded7d8c3e94b57720ddbdafa0d731b732acdffbc
                                              │
                            Contains (24 blocks in IPFS CAR v1):
                            ├── README.txt (recovery guide)
                            ├── README_recover.txt (中文恢复步骤)
                            ├── token_index.json (258KB) ← 核心索引
                            ├── arweave_cid_map.csv (113KB)
                            ├── arweave_cid_map.jsonl (153KB)
                            ├── verify_batch_report.csv (41KB)
                            ├── fallback_media_report.csv (18KB)
                            ├── SHA-256 checksums
                            └── tools/ (upload/verify scripts)
                                              │
                                              ▼
                            token_index.json
                            4 contracts → 175 NFTs → 434 unique Arweave txids
                                              │
                            ┌─────────────────┼─────────────────┐
                            ▼                 ▼                 ▼
                       175 metadata       259 media CARs    (no media)
                       CARs               (image.png,
                       (NFT JSON)          animation.mp4,
                                           etc.)
                            │                 │
                            ▼                 ▼
                       Each CAR on Arweave:
                       metadata: arweave.net/<txid>  (1~20KB each)
                       media:    arweave.net/<txid>  (0.1~120MB each)
```

## Contract Breakdown

| Contract Address | NFT Count | Description |
|-----------------|-----------|-------------|
| `0x019372bBee377109b8Eae66d7267f5C4EaAdBb79` | 156 | ASIMilestones Chronicle NFTs |
| `0x2b0c3cc5CD9652BEf0caCFc9c7699455725B9cc1` | 16 | (contract 2) |
| `0xF12815D22BAf904A21B498a5dF8e5d8529d2079e` | 2 | (contract 3) |
| `0x74f97bDEfa07C2F99c876C2Bd3b49628EdD1c603` | 1 | (contract 4) |
| **Total** | **175** | |

## NFT Data Structure (per NFT)

Each NFT in token_index.json has:
```json
{
  "metadata": {
    "root_cid": "bafkrei...",          // IPFS CID of the NFT metadata JSON
    "txid": "W-yhyFDGA...",            // Arweave txid of the CAR file
    "car_sha256": "3c7ce5c0...",       // SHA-256 of the CAR file
    "car_size": 3158,                  // CAR file size in bytes
    "url": "https://arweave.net/..."   // Direct download URL
  },
  "media": [
    {
      "root_cid": "bafybeia...",       // IPFS CID of the media file
      "leaf_path": "image.png",        // filename in the DAG
      "txid": "c-xViE37...",           // Arweave txid
      "car_sha256": "b605487a...",     // SHA-256 of the CAR
      "car_size": 2081997,             // ~2MB
      "url": "https://arweave.net/...",
      "match": "exact"                 // verification status
    },
    {
      "root_cid": "bafybeia...",
      "leaf_path": "animation.mpga",
      "txid": "I_Lli-i6...",
      "car_sha256": "0f706eb9...",
      "car_size": 4945501,             // ~5MB
      "url": "https://arweave.net/...",
      "match": "exact"
    }
  ]
}
```

## GitHub Release Backup Plan

### Release: `nft-backup-v1` (already exists, 822MB)

Contains 9 tar.gz archives of bulk-downloaded CAR files from Arweave:
- nft-cars-part01~09.tar.gz (50 CARs each)
- nft-cars-manifest.tar.gz

### New Release: `nft-individual-v1` (planned)

Each NFT as an individual release asset:
```
nft-<contract>-<token_id>.tar.gz
  ├── metadata.car
  ├── image.png.car (if exists)
  ├── animation.mp4.car (if exists)
  └── manifest.json (txid, sha256, size, verification)
```

### Or: Organized by contract
```
nft-0x019372bB-part01.tar.gz  (NFTs 1-50)
nft-0x019372bB-part02.tar.gz  (NFTs 51-100)
nft-0x019372bB-part03.tar.gz  (NFTs 101-156)
nft-0x2b0c3cc5.tar.gz         (16 NFTs)
nft-0xF12815D2.tar.gz         (2 NFTs)
nft-0x74f97bDE.tar.gz         (1 NFT)
```

## Verification Command

```bash
# Download and verify any single NFT's CAR:
curl -sL "https://arweave.net/<txid>" -o /tmp/nft.car
sha256sum /tmp/nft.car  # should match car_sha256 from token_index.json

# Import to IPFS:
ipfs dag import /tmp/nft.car
```

## Summary

The provenance chain is:

1. **Bitcoin BIP-340 signature** (valid) signs `authority.jcs.json`
2. `authority.jcs.json` references **Arweave documents** including the primary verification archive
3. The **recovery-package.bin** (on Arweave) contains `token_index.json`
4. `token_index.json` maps **175 NFTs → 434 individual Arweave CAR files**
5. Each CAR file has **SHA-256 verification** and is independently downloadable

**Every single NFT has its own Arweave backup, not a bulk backup.**
