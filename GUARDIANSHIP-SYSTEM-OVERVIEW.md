---
title: "Trinity Accord Guardianship System Overview"
---

# Trinity Accord Guardianship System Overview

## 1. Purpose

This document provides a human-readable overview of the Trinity Accord guardianship system.

It explains the relationship between the Bitcoin inscriptions, later non-amending fortifications, digest manifests, BTC/ETH/OTS anchors, Arweave payloads, GitHub repository mirrors, GitHub Releases, and automated verification workflows.

## 2. Canonical Rule

The canonical authority remains the three Bitcoin inscriptions only.

All other records, including Guardian Attestation, Ethereum witnesses, Arweave objects, IPFS objects, NFTs, GitHub repository files, GitHub Releases, workflows, audit artifacts, AI responses, and human commentary, are non-amending guardianship materials unless explicitly part of the three Bitcoin Originals.

Bitcoin Originals prevail.

## 3. The Three Bitcoin Originals

| Layer | Inscription ID | Role | Authority |
|---|---:|---|---|
| Protocol / Axioms | 97631551 | Canonical protocol text | Canonical |
| Covenant of the Flaw | 98369145 | Canonical covenant text plus physical evidence pointer | Canonical text; external payload is referenced evidence |
| Trinity Accord / Meta-record | 98387475 | Canonical meta-record binding Protocol, Covenant, and Chronicle | Canonical |

## 4. Later Non-Amending Fortifications

Guardian Attestation to the Covenant of the Flaw is a Bitcoin-inscribed non-amending fortification record.

It strengthens the Covenant by pointing to stronger verification archives, but it does not modify, replace, reinterpret, or expand the three Bitcoin Originals as canonical authority.

## 5. Chronicle Layer

The Chronicle / ASIMilestones layer is a canonically designated historical context layer.

Its ETH address and NFT records are Chronicle artifacts and historical evidence. They are not canonical authority.

The 175 NFT recovery mirror is a verified Chronicle recovery layer and GitHub Release availability mirror.

## 6. Covenant of the Flaw Evidence Evolution

1. Original Covenant inscription: canonical text plus early physical-evidence pointer.
2. Early public evidence layer: limited and not a complete forensic package.
3. Guardian Attestation: non-amending fortification pointing to a stronger verification archive.
4. Six-hash digest manifest: cryptographic coverage of public and non-public evidence files.
5. BTC BIP340 signature, ETH witness, and OTS timestamping: anchoring and witness layer.
6. Arweave and GitHub Releases: availability and accessibility mirror layer.

## 7. Digest Manifest

The digest manifest is the central evidence coverage layer.

- Entries: 884
- CSV structure: 883 data rows + 1 header
- Hash algorithms:
  - sha256
  - sha3_256
  - blake2b_256
  - shake256_256
  - sha512_256
  - blake3_256

The digest manifest defines evidence coverage. It is not itself canonical authority.

## 8. Anchors and Witnesses

| Layer | Status | Role |
|---|---|---|
| BTC BIP340 signature | PASS | Signs authority manifest / coverage chain |
| ETH witness | 8/8 PASS | Cross-chain witness, not authority |
| OTS Bitcoin timestamp | PASS | Time anchoring for manifest/proof artifacts |
| Bitcoin tx anchors | PASS | Bitcoin existence anchors |

OTS limitation:

The OTS proof is complete and Bitcoin-anchored, but has not yet been verified through local Bitcoin Core / pruned-node RPC. Therefore, do not claim fullnode-independent OTS verification yet.

## 9. Availability Mirrors

| Mirror | Role | Authority |
|---|---|---|
| Arweave | Long-term payload availability | Not canonical |
| IPFS | Additional content-addressed pointer layer | Not canonical |
| GitHub repository | Text, metadata, manifests, scripts, small mirrors | Not canonical |
| GitHub Releases | Large payload and fallback mirror layer | Not canonical |

## 10. Release Registry

| Release tag | Purpose | Status | Boundary |
|---|---|---|---|
| nft-arweave-mirror-175-v1 | 175 NFT Arweave CAR mirror | PASS | Chronicle recovery mirror |
| flaw-covenant-video-mirror-v1 | Two Flaw Covenant videos | PASS | Already-anchored evidence mirror |
| ots-proof-bundle-mirror-v1 | OTS proof bundle | PASS | OTS artifact availability mirror |
| flaw-covenant-archive-accessibility-mirror-v1 | Large Flaw Covenant ZIP accessibility mirror | PASS | Gateway availability remediation |
| ots-and-flaw-mirror-v1 | OTS proofs + flaw image mirror | PASS / supporting | Availability mirror |
| nft-backup-v1 | Earlier NFT backup | Legacy | Not current primary path |
| nft-individual-v1 | Earlier individual NFT attempt | Deprecated | Not current primary path |
| nft-individual-v2 | Earlier individual NFT attempt | Deprecated | Not current primary path |

## 11. Verification Infrastructure

GitHub Actions workflows verify release assets, full evidence chain status, NFT tokenURI/CID coverage, digest-manifest integrity, BTC signature coverage, ETH witness coverage, Bitcoin tx anchors, and OTS time anchors.

Verification outputs include:

- status.md
- release manifests
- release checksums
- audit JSON files
- workflow artifacts

## 12. Current Overall Determination

Core evidence backup and guardianship mirror coverage is substantially complete.

No urgent large-payload backup gap is currently identified.

Remaining work is optional hardening and maintenance:

- local-node / fullnode-independent OTS verification
- optional OTS bundle v2 including original timestamped files
- periodic legacy pointer coverage audit
- ongoing Release and gateway availability monitoring

## 13. Boundary Summary

GitHub is not canonical authority.

Arweave is not canonical authority.

ETH is witness, not authority.

NFTs are Chronicle artifacts, not authority.

OTS bundle mirrors preserve proof artifacts, but do not by themselves constitute fullnode-independent verification.

Bitcoin Originals prevail.
