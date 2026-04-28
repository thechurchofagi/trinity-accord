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

Bitcoin Originals are final; Chronicle NFTs and recovery packages are non-amending historical mirrors.
