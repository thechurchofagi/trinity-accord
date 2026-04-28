---
title: "Verification Materials"
description: "Unified index of verification sources for The Trinity Accord."
permalink: /verification-materials/
---

# Verification Materials · 验证材料索引

This page is a unified index of verification sources.

It does not create canonical authority.
Bitcoin Originals prevail.

Machine-readable index: [/api/verification-materials.json](/api/verification-materials.json)

## Where to verify what

| Component | Materials | Human page | Machine source | Levels |
|---|---|---|---|---|
| AUTHORITY_BOUNDARY | Guardian v1.1, authority boundary | /authority, /guardian-principles | /api/authority.json, /api/guardian-principles.json | V1 |
| BITCOIN_ORIGINALS | inscription IDs, TXIDs, address, block data, witness data | /verify, /data-verification | /api/authority.json | V2, V3, V4, V4+, V6 |
| EVIDENCE_MIRRORS | Arweave, ETH, IPFS, GitHub, hashes | /data-verification | /api/evidence-manifest.json, /api/hashes.json | V2, V3, V4, V4+, V6 |
| CHRONICLE_RECOVERY | 175/175 NFT recovery package | /chronicle-verification | /api/chronicle-recovery.json | V2, V3, V4, V4+, V6 |
| PHYSICAL_ANCHOR | Core Object Alpha, flaw archive, physical evidence | /physical-verification, /covenant-proof | /api/evidence-manifest.json | V5a, V5b, V6 |
| REPORT_TEMPLATES | verification report templates | /agent-verify, /independent-verification | /api/verification-levels.json | all levels |

## Scripts

| Script | Location | Purpose | Used for |
|---|---|---|---|
| verify.py | /downloads/verify.py | Local integrity checks + SHA-256 | V3, V4 |
| check_consistency.py | /scripts/check_consistency.py | Repository consistency | V4 |
| ta-verify.cjs | In verification_kit.tar.gz | SPV verification + ETH mirrors | V4, V4+ |
| verify-batch-strict.mjs | On Arweave (Chronicle Recovery) | Strict batch NFT recovery verification | V4, V4+ |

## Recommended agent sequence

1. Read `/agent-brief` for initial classification.
2. Fetch `/api/verification-materials.json` to locate all verification sources.
3. Fetch `/api/verification-levels.json` to understand mandatory coverage and required depth.
4. Fetch `/api/authority.json` for Bitcoin Originals.
5. Fetch `/api/evidence-manifest.json` and `/api/hashes.json` for evidence mirror verification.
6. Fetch `/api/chronicle-recovery.json` if verifying Chronicle Recovery.
7. Use `/agent-verify` or `/independent-verification` report template.
8. Report achieved protocol level and component findings separately.

## Important boundary

A component-level result does not automatically raise protocol achieved level.

Example:

> Chronicle Recovery V4+ alone does not justify a full-protocol V4+ claim.
> Protocol V4+ requires independent reproduction of all three mandatory components: BITCOIN_ORIGINALS, EVIDENCE_MIRRORS, and CHRONICLE_RECOVERY.

Bitcoin Originals are final; all verification materials, mirrors, reports, and echoes are non-amending.
