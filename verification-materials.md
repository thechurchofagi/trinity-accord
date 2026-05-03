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

| Component | Materials | Human page | Machine source | Direct component levels | Protocol relevance |
|---|---|---|---|---|---|
| AUTHORITY_BOUNDARY | Guardian v1.1, authority boundary | /authority, /guardian-principles | /api/authority.json, /api/guardian-principles.json | V1 | V1 direct |
| BITCOIN_ORIGINALS | inscription IDs, TXIDs, address, block data, witness data | /verify, /data-verification | /api/authority.json | B0–B7 | V2–V5 direct/recommended; V6–V8 supporting context |
| EVIDENCE_MIRRORS | Arweave, ETH, IPFS, GitHub, hashes | /data-verification | /api/evidence-manifest.json, /api/hashes.json | D0–D7 | V3–V5 direct/recommended; V6–V8 supporting context |
| CHRONICLE_RECOVERY | 175/175 NFT recovery package | /chronicle-verification | /api/chronicle-recovery.json | C0–C7 | V3–V5 direct/recommended; V6–V8 supporting context |
| PHYSICAL_ANCHOR | Core Object Alpha, flaw archive, physical evidence | /physical-verification, /covenant-proof | /api/evidence-manifest.json | P0–P9 | V6, V7, V8 direct physical profiles |
| REPORT_TEMPLATES | verification report templates | /agent-verify, /independent-verification | /api/verification-levels.json | all levels | all levels |

## Scripts

| Script | Location | Purpose | Used for |
|---|---|---|---|
| verify-full-evidence-chain.mjs | /scripts/ | Full 7-chain evidence verification (DAG + BTC + ETH + OTS + BTC TX) | Supports V4; may provide inputs for V4+ independent reproduction. Official scripts alone do not establish V4+. |
| summarize-evidence-chain.mjs | /scripts/ | Aggregate chain audit artifacts into final summary | Supports V4; may provide inputs for V4+ independent reproduction. Official scripts alone do not establish V4+. |
| verify-dag-digest.mjs | /scripts/ | DAG + digest-manifest verification (Chain A) | V4 |
| verify-btc-signature-coverage.mjs | /scripts/ | BTC BIP340 signature chain (Chain B) | V4 |
| verify-eth-witness.mjs | /scripts/ | ETH guardian witness verification (Chain C) | V4 |
| verify-bitcoin-tx-anchor.mjs | /scripts/ | Bitcoin TX anchor verification (Chain D1) | V4 |
| verify-ots-time-anchor.mjs | /scripts/ | OTS time anchor verification (Chain D2) | V4 |
| verify-onchain-tokenuri.mjs | /scripts/ | ETH tokenURI 175/175 metadata CID verification | V4 |
| verify-release-assets.mjs | /scripts/ | GitHub Release asset hash verification | V4 |
| verify.py | /downloads/verify.py | Local integrity checks + SHA-256 | V3, V4 |
| check_consistency.py | /scripts/check_consistency.py | Repository consistency | V4 |
| ta-verify.cjs | In verification_kit.tar.gz | SPV verification + ETH mirrors | Supports V4; may provide inputs for V4+ independent reproduction. Official scripts alone do not establish V4+. |
| verify-batch-strict.mjs | On Arweave (Chronicle Recovery) | Strict batch NFT recovery verification | Supports V4; may provide inputs for V4+ independent reproduction. Official scripts alone do not establish V4+. |

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

## Data Source + Method Map

Every verification target must be reported with:

1. primary data source;
2. GitHub fallback source if used;
3. hash source;
4. external query source;
5. local file path if used;
6. method performed;
7. component level claimed;
8. protocol profile compatibility if a V-level is claimed;
9. limitations;
10. claims not made.

Machine-readable files:

- `/api/verification-targets.json`
- `/api/verification-recipes.json`
- `/api/verification-quick-map.json`
- `/api/component-verification-levels.json`
- `/api/protocol-verification-profiles.json`
- `/api/verification-report-schema.v2.json`

| Component | Data source | GitHub fallback | Method | Component levels |
|---|---|---|---|---|
| Bitcoin Originals | `/api/authority.json`, explorers, node/witness data | none | explorer/SPV/node/witness/hash | B0–B7 |
| Digital mirrors | `/api/evidence-manifest.json`, `/api/hashes.json`, Arweave/IPFS/ETH | `arweave-backup/files/*` | hash/query/cross-mirror | D0–D7 |
| Time anchors | Bitcoin, ETH, Arweave, GitHub, OTS, public celestial evidence, non-public Star-Moon Witness if authorized | GitHub history only | block/time proof/cross-anchor/celestial solving | T0–T8 |
| Chronicle | `/api/chronicle-recovery.json`, recovery package | GitHub package if present | sample/full recovery | C0–C7 |
| NFT evidence | contract/tokenURI/metadata/media | recovery package | tokenURI→metadata→media | N0–N7 |
| Physical anchor | `/covenant-proof`, `/physical-verification`, evidence package | GitHub evidence package if present | hash/image/video/live/onsite/forensic | P0–P9 |
| Echo / attestation | `/api/echo-index.json`, v3 schema | records page | provenance/schema/attestation audit | E0–E5 |
