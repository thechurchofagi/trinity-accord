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

BTC BIP340 signature, ETH witness, and OTS Bitcoin timestamping strengthen the digest-manifest layer. Arweave, GitHub repository, and GitHub Releases now provide verified availability mirrors.

Remaining work is documentation-level relationship mapping and optional hardening, not urgent large-payload backup.

## Corrected Audit Facts

| Item | Correct Value |
|---|---|
| digest-manifest coverage | 884 entries |
| CSV structure | 883 data rows + 1 header |
| Guardian Attestation | Bitcoin-inscribed non-amending fortification |
| ETH witness verification | 8/8 PASS |
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
| 175 NFT recovery records | Manifest / recovery coverage | Arweave CAR sources | token_index / provenance | nft-arweave-mirror-175-v1 | PASS | Chronicle recovery layer |
| ETH witness records | 8/8 verification PASS | Not primary | archive/eth-witness | Not required | PASS | Witness, not authority |
| Full evidence chain | Workflow PASS | Inputs verified | scripts / status | audit artifacts | PASS | Verification result, not authority |

## Release Registry

| Release tag | Purpose | Custom evidence assets | Status | Boundary |
|---|---:|---:|---|---|
| nft-arweave-mirror-175-v1 | 175 NFT Arweave CAR mirror | Expected 177 custom assets | PASS | Chronicle recovery mirror |
| flaw-covenant-video-mirror-v1 | Two flaw videos mirrored from Arweave | 5/5 | PASS | Already-anchored evidence mirror |
| ots-proof-bundle-mirror-v1 | OTS proof bundle mirror | 4/4 | PASS | OTS artifact availability mirror |
| ots-and-flaw-mirror-v1 | OTS proofs + flaw image mirror | Existing release | PASS / legacy supporting mirror | Availability mirror |
| flaw-covenant-archive-accessibility-mirror-v1 | Large Flaw Covenant ZIP accessibility mirror | 5/5 | PASS | Non-amending accessibility mirror for gateway availability mitigation |
| nft-backup-v1 | Earlier NFT backup | Legacy | Legacy | Not current primary path |
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

The 175 NFT GitHub Release mirror is a verified availability mirror for Chronicle recovery records.

## Arweave Documentation Mirrors

| Object | TXID | Status | Boundary |
|---|---|---|---|
| Guardianship system docs v1 | I0xNBwbgaGsODjnK5ze25sOwV9V8i7FtKe-8upRoohw | PASS | Documentation mirror only; not canonical authority |

## Final Determination

Core evidence backup coverage is substantially complete.

There are no urgent large-payload backup gaps currently identified. Remaining work is primarily documentation-level relationship mapping, periodic coverage audits, and optional hardening such as a self-contained OTS bundle v2.
