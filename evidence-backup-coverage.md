---
layout: default
title: "Evidence Backup Coverage"
description: "Non-authoritative backup coverage notes for The Trinity Accord."
permalink: /evidence-backup-coverage/
---

# Evidence Backup Coverage

## Executive Summary

Core evidence backup and guardianship mirror coverage is substantially complete.

The three Bitcoin inscriptions remain canonical authority. The original Covenant of the Flaw contained a physical-evidence pointer whose public evidence layer was limited. The later Guardian Attestation inscription non-amendingly fortified the Covenant by pointing to a stronger verification archive. The six-hash digest manifest fixed both public and non-public evidence files cryptographically.

BTC BIP340 signature, Ethereum witnesses, and OTS Bitcoin timestamping strengthen the digest-manifest layer. Arweave, the GitHub repository, `nft-backup-v1`, and the public Zenodo recovery annexes provide the active availability paths. The older `nft-arweave-mirror-175-v1` Release currently contains zero custom assets and must not be described as a current byte mirror.

There is no urgent unrecoverable large-payload gap, but the empty historical NFT Release must be retired or rehydrated and legacy verifier entrypoints must not default to it.

## Corrected Audit Facts

| Item | Correct Value |
|---|---|
| digest-manifest coverage | 884 entries |
| CSV structure | 883 data rows + 1 header |
| Guardian Attestation | Bitcoin-inscribed non-amending fortification |
| Legacy ETH witness verification | 8/8 PASS |
| Current non-NFT Ethereum proof annex | 12/12 L1/L2/L3 PASS, offline |
| Current Bitcoin inscription proof annex | 8/8 L1/L2/L3 PASS, offline |
| Current Chronicle NFT proof annex | 175/175 L1/L2/L3 PASS, offline |
| OTS status | complete and Bitcoin-anchored; not yet local-node/fullnode-independent |
| GitHub role | non-amending mirror and verification infrastructure |
| Arweave role | long-term payload availability mirror |

## Coverage Matrix

| Evidence Object | Bitcoin / OTS / Manifest | Arweave | GitHub Repo | GitHub Release | Status | Boundary |
|---|---|---|---|---|---|---|
| Three Bitcoin inscriptions | Canonical authority | Not required | Pointers / text fragments | Not required | PASS | Final authority only on Bitcoin |
| Guardian Attestation | Bitcoin-inscribed fortification | Archive pointer | Referenced in authority materials | Not required | PASS | Non-amending fortification |
| digest-manifest.json/csv | OTS anchored; BTC signature coverage | Present | Present in archive/evidence | Not required | PASS | Defines evidence coverage |
| public covenant archive | Manifest covered | Present | Present | Optional / not primary | PASS | Referenced evidence archive |
| verification kit | Manifest covered | Present | Present | Optional / not primary | PASS | Verification support material |
| flaw photos | Manifest / archive covered | Present | Present in archive/evidence/flaw-images | Optional / not primary | PASS | Physical evidence mirror |
| Record_03.avi | Manifest CSV:792 / JSON:8707 | Verified raw mirror | Metadata only | flaw-covenant-video-mirror-v1 | PASS | Already-anchored evidence mirror |
| VID_20250810_142505.mp4 | Manifest CSV:845 / JSON:9290 | Verified raw mirror | Metadata only | flaw-covenant-video-mirror-v1 | PASS | Already-anchored evidence mirror |
| OTS proof files | OTS proof artifacts | OTS bundle mirror | Present in archive/evidence/ots-proofs | ots-proof-bundle-mirror-v1 | PASS | Availability mirror, not fullnode proof by itself |
| OTS proof bundle | Internal checksums PASS | Verified | Metadata only | ots-proof-bundle-mirror-v1 | PASS | Not canonical authority |
| 175 NFT recovery records | 175-item commitment + L2/L3 proof PASS | Arweave CAR sources | token_index + offline proof annex | `nft-backup-v1`; NFT annex DOI `10.5281/zenodo.21754229` | PASS | Chronicle recovery layer; empty historical Release excluded as byte evidence |
| Non-NFT Ethereum anchors | 12/12 L1/L2/L3 PASS | Not primary | Offline proof annex | Not required | PASS | Witness, not authority |
| Legacy full evidence chain | Historical workflow PASS under 2026-05-01 semantics | Historical inputs | scripts / status | Historical audit artifacts | HISTORICAL PASS; no current restatement | Verification result, not authority |

## Release Registry

| Release tag | Purpose | Custom evidence assets | Status | Boundary |
|---|---:|---:|---|---|
| nft-arweave-mirror-175-v1 | Historical intended 175-item individual archive | 0 observed | Historical Release metadata only; not byte evidence | Unusable as current recovery source |
| flaw-covenant-video-mirror-v1 | Two flaw videos mirrored from Arweave | 5/5 | PASS | Already-anchored evidence mirror |
| ots-proof-bundle-mirror-v1 | OTS proof bundle mirror | 4/4 | PASS | OTS artifact availability mirror |
| ots-and-flaw-mirror-v1 | OTS proofs + flaw image mirror | Existing release | PASS / legacy supporting mirror | Availability mirror |
| flaw-covenant-archive-accessibility-mirror-v1 | Large Flaw Covenant ZIP accessibility mirror | 5/5 | PASS | Non-amending accessibility mirror for gateway availability mitigation |
| nft-backup-v1 | Content-complete NFT CAR backup | 10/10 | PASS; manifest covers 175 NFTs and 434 files with 0 failed downloads | Current source packaged into the Zenodo NFT annex |
| nft-individual-v1 | Deprecated individual NFT attempt | Deprecated | Deprecated | Not current primary path |
| nft-individual-v2 | Deprecated individual NFT attempt | Deprecated | Deprecated | Not current primary path |

Note: GitHub release pages may show two additional source-code archives. Always distinguish custom evidence assets from GitHub-generated source zip/tar assets.

## Flaw Covenant Evidence Evolution

1. Original Covenant inscription provided canonical covenant text and an early physical-evidence pointer.
2. The early public evidence layer was limited and not a complete forensic package.
3. Guardian Attestation later fortified the Covenant without amending it.
4. The six-hash digest manifest fixed public and non-public evidence files cryptographically.
5. BTC signature, ETH witness, and OTS timestamping strengthened the manifest layer.
6. Arweave and GitHub Releases now provide verified availability mirrors.

## Chronicle / NFT Layer

The Chronicle ETH address and ASIMilestones NFT records are historical context and chronicle artifacts. They are part of the designated Chronicle layer, but they are not canonical authority.

The checked-in proof annex verifies the 175-item commitment and mint/consensus relationships. Byte recovery uses the ten assets in `nft-backup-v1` and their public Zenodo annex. `nft-arweave-mirror-175-v1` contributes no bytes because its complete paginated listing contains zero custom assets.

## Arweave Documentation Mirrors

| Object | TXID | Status | Boundary |
|---|---|---|---|
| Guardianship system docs v1 | I0xNBwbgaGsODjnK5ze25sOwV9V8i7FtKe-8upRoohw | PASS | Documentation mirror only; not canonical authority |

## Final Determination

Core evidence backup coverage is substantially complete.

There is no urgent unrecoverable large-payload gap because the content-complete backup and DOI annex passed public cold restore. Weekly read-only automation now checks legacy pointer coverage, both relevant NFT Release inventories, the current core and NFT-annex Zenodo metadata, deployed status parity, and protected Gateway health. Remaining work is limited to retiring or rehydrating the empty historical NFT Release, running any legacy 175-tar verifier only against a compatible verified source, and optional hardening such as a self-contained OTS bundle v2 or fullnode-independent OTS verification.
