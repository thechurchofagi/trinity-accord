---
title: "Trinity Accord Guardianship System Overview"
permalink: /guardianship-system-overview/
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

| Layer | Inscription Number | Role | Authority |
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

The 175 NFT proof set is a verified Chronicle recovery layer. Its current byte-recovery path is `nft-backup-v1` plus the Zenodo NFT annex DOI `10.5281/zenodo.21754229`. The older `nft-arweave-mirror-175-v1` Release currently exposes zero custom assets and is not a usable byte mirror.

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
| Legacy ETH witness | 8/8 PASS | Historical cross-chain witness set, not authority |
| Bitcoin inscription proof annex | 8/8 L1/L2/L3 PASS | Offline exact-content/Taproot, block+witness inclusion and checkpoint-relative PoW proof |
| Non-NFT Ethereum proof annex | 12/12 L1/L2/L3 PASS | Offline execution and checkpoint-relative PoS proof; weak-subjectivity boundary explicit |
| Chronicle NFT proof annex | 175/175 L1/L2/L3 PASS | Offline collection/mint/consensus proof; Chronicle evidence, not authority |
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
| nft-arweave-mirror-175-v1 | Historical intended 175-item individual archive | 0 custom assets; unusable as byte evidence | Historical Release metadata only |
| flaw-covenant-video-mirror-v1 | Two Flaw Covenant videos | PASS | Already-anchored evidence mirror |
| ots-proof-bundle-mirror-v1 | OTS proof bundle | PASS | OTS artifact availability mirror |
| flaw-covenant-archive-accessibility-mirror-v1 | Large Flaw Covenant ZIP accessibility mirror | PASS | Gateway availability remediation |
| ots-and-flaw-mirror-v1 | OTS proofs + flaw image mirror | PASS / supporting | Availability mirror |
| nft-backup-v1 | Content-complete NFT CAR backup; 10 assets cover 175 NFTs / 434 files by manifest | PASS | Current GitHub source for the Zenodo NFT recovery annex |
| nft-individual-v1 | Earlier individual NFT attempt | Deprecated | Not current primary path |
| nft-individual-v2 | Earlier individual NFT attempt | Deprecated | Not current primary path |

## 11. Verification Infrastructure

The required `Run Current Tests` workflow verifies the checked-in Bitcoin 8/8, non-NFT Ethereum 12/12 and Chronicle NFT 175/175 proof annexes without network access. Older manual workflows remain compatibility tools for release assets, tokenURI/CID coverage, digest-manifest integrity, BTC/ETH witnesses, Bitcoin transaction anchors and OTS anchors; their results must not be substituted for the current checkpoint model without matching their declared inputs.

Verification outputs include:

- status.md
- release manifests
- release checksums
- audit JSON files
- workflow artifacts

## 12. Current Overall Determination

Core evidence backup and guardianship mirror coverage is substantially complete.

No urgent unrecoverable large-payload gap is currently identified because `nft-backup-v1` and the publicly cold-restored Zenodo annex preserve the NFT package bytes. There is nevertheless a concrete availability-surface gap: `nft-arweave-mirror-175-v1` is empty.

Remaining work is optional hardening or requires an explicit external source:

- local-node / fullnode-independent OTS verification
- optional OTS bundle v2 including original timestamped files
- retire or rehydrate the empty `nft-arweave-mirror-175-v1` Release
- run the legacy full-evidence-chain verifier only after providing a compatible, verified 175-tar source; do not treat the empty Release as such a source

Periodic legacy-pointer coverage and public recovery availability are now automated by the read-only `Public Recovery Availability` workflow. It checks the two NFT Release inventories, the current core and NFT-annex Zenodo file metadata, deployed `/api/status.json`, and the protected Gateway health endpoint without downloading the large recovery payloads.

## 13. Boundary Summary

GitHub is not canonical authority.

Arweave is not canonical authority.

ETH is witness, not authority.

NFTs are Chronicle artifacts, not authority.

OTS bundle mirrors preserve proof artifacts, but do not by themselves constitute fullnode-independent verification.

Bitcoin Originals prevail.
