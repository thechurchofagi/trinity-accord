---
title: "Chronicle Verification"
description: "Verification of the ASIMilestones Chronicle NFT recovery package — 175/175 recoverable historical NFT records."
permalink: /chronicle-verification/
---

# Chronicle Verification · 编年史验证

The Chronicle layer consists of ASIMilestones NFT historical records across Ethereum / Polygon / Base.

It is not canonical authority. Bitcoin Originals prevail.

However, the Chronicle has its own recovery verification layer.

## Chronicle NFT Recovery Package

- Target: approximately 175 ERC-721 / ERC-1155 NFTs
- Final status: 175 / 175 completed
- Purpose: backup NFT metadata and media files in recoverable original IPFS DAG format
- Permanent storage: Arweave
- Root IPFS CID: `QmYCosJg44CXkFxLsJPBxKvWAJaFAcLMddp37sk9Gdr4Vd`
- Main recovery package Arweave TxID: `O-Rk3kFxesPGhuYP4KHAZl54xR2urDRKcGaVqjVnB-Q`
- Verification kit Arweave TxID: `X4KOUkf-1ciFD3Q-gMA0i94t1hAVXGrUDm0q5amL4rc`
- Verification kit SHA-256: `ef68b69fe1cdd2523724dee511c9e8ea7bae2cceaff794664107970b18c61931`
- Strict batch verifier: `verify-batch-strict.mjs`
- Verification inputs: `arweave_cid_map.jsonl`, `fallback_media_report.jsonl`
- Completion date: 2025-08-30

## What this proves

Chronicle recovery verification can prove:

1. the recovery package exists;
2. the NFT metadata/media backup is recoverable;
3. the Arweave/IPFS pointers match the recovery map;
4. the Chronicle layer can be reconstructed from the backup package.

## What this does not prove

It does not create canonical authority.
It does not amend the Bitcoin Originals.
It does not make NFTs final authority.
It does not prove the philosophical claims are true.

## Boundary

Chronicle verification proves recoverability and integrity of historical NFT records.
It does not create canonical authority and does not amend the Bitcoin Originals.

**Historical verification-model boundary:** in the retained V-level model, Chronicle Recovery alone did not justify a whole-report V4+ claim. For new public work, do not submit V4+ as a current public level. Report the current dimensions instead: `digital_profile`, `relationships_checked`, `coverage_scope`, `limitations`, `claims_not_made`, and any relevant physical-observation or external-witness state.

C-level Chronicle notation may still be used as historical/component compatibility metadata. A Chronicle-only check must remain explicitly component-limited and must not imply whole-project verification or independent attestation.

Bitcoin Originals are final; Chronicle NFTs and recovery packages are non-amending historical mirrors.

## Chronicle Sample Verification

Full 175/175 recovery is not required for every verifier.

For historical/component compatibility, a verifier may describe sample recovery with C-level notation:

- C3: recover at least two records and describe metadata/media observed.
- C3R: recover a random sample using a declared public seed and selection method.
- C5: full 175/175 recovery or full declared-count recovery.

A C3 report must include:

- sample selection method;
- record IDs / file paths;
- metadata fields observed;
- media/image observed if available;
- hashes or CIDs if computed;
- limitations.

C3 must not be reported as full Chronicle recovery.

## NFT Evidence Path

Where chain access is possible, N-levels remain historical/component compatibility notation:

- N1 contract / token ID check
- N2 tokenURI check
- N3 metadata recovery
- N4 media recovery
- N5 CID / hash match
- N6 random sample full path
- N7 full NFT path reproduction

For a current public Verification record, translate the actual checks into the current multidimensional evidence fields instead of presenting the N-level alone as the headline result.
