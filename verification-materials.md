---
title: "Verification Materials"
description: "Unified index of verification sources for The Trinity Accord."
permalink: /verification-materials/
---

# Verification Materials · 验证材料索引

<!-- current-model-policy-v1 -->
> **Current interpretation and verification model:** The Chronicle has no current fixed five-stage, seven-stage, or other fixed-stage periodization. Use objective chronology, quarter navigation, overlapping categories, and explicitly provisional interpretation. New verification reports separate digital profile, evidence relationships, physical observation, and external witness; V4+/V6/V7/V8 are historical-only labels. See `/interpretation-verification-model/`, `/api/interpretation-model-policy.v1.json`, and `/api/verification-claim-model.v1.json`.


This page is a unified index of verification sources.

It does not create canonical authority. Bitcoin Originals prevail.

## Start with the evidence relationship, not a level number

Before verifying, read:

- Human guide: [`/EVIDENCE-RELATIONSHIP-GUIDE.md`](/EVIDENCE-RELATIONSHIP-GUIDE.md)
- Machine evidence graph: [`/api/evidence-relationship-map.v1.json`](/api/evidence-relationship-map.v1.json)
- Preferred verification profiles: [`/api/verification-profiles.v1.json`](/api/verification-profiles.v1.json)
- Preferred context profiles: [`/api/context-action-profiles.v1.json`](/api/context-action-profiles.v1.json)
- Corrections and supersession: [`/api/corrections-index.json`](/api/corrections-index.json)

Machine-readable material index: [/api/verification-materials.json](/api/verification-materials.json)

## Preferred verification profiles for new reports

| Profile | Minimum meaning |
|---|---|
| `context_only` | Sources read; no technical verification performed |
| `reference_checked` | A primary or external reference was actually queried |
| `integrity_checked` | Bytes, hashes, signatures, SPV/OTS proofs, or equivalent integrity data were computed or validated |
| `independent_reproduction` | A material result was reproduced without merely trusting official output |
| `full_public_digital` | All declared public digital target families were checked and unavailable targets listed |

Report two other dimensions separately:

- `physical_observation`: none, public media, remote live, onsite, or forensic;
- `external_witness`: none, notarial scope, independent report, institutional attestation, or regulatory/court record.

A high physical or notarial finding does not automatically raise the digital profile.

## What operation are you performing?

| Operation | Question answered | Typical evidence |
|---|---|---|
| Reference | Does the named transaction, object or pointer exist at the stated location? | explorer/RPC/gateway query |
| Hash | Are these bytes identical to the committed bytes? | expected digest + local recomputation |
| Signature | Did the holder of this key sign this digest/typed statement? | BIP-340 or EIP-712 validation |
| Timestamp | Did this digest exist no later than the attested block? | Bitcoin/OTS proof |
| Mirror | Can the bytes be independently retrieved from another location? | Arweave, IPFS, GitHub Release |
| Witness | Was a statement placed on a secondary public chain? | ETH witness transaction |
| Notarization | What process/document/date/identity was recorded in the notarial act? | Shenzhen notarial certificate and preservation records |
| Physical observation | What did the verifier actually observe about the object? | public media, remote live, onsite, forensic report |

Do not use the unqualified word `verified`; state the operation and target.

## Where to verify what

| Component | Materials | Human page | Machine source | Preferred result |
|---|---|---|---|---|
| AUTHORITY_BOUNDARY | Three Originals, Guardian v1.1, authority boundary | `/authority`, `/guardian-principles` | `/api/authority.json` | boundary-correct context or reference result |
| BITCOIN_ORIGINALS | inscription IDs, TXIDs, address, blocks, witness/body bytes | `/verify`, `/data-verification` | `/api/authority.json` | reference / integrity / independent reproduction |
| EVIDENCE_MIRRORS | Arweave, ETH, IPFS, GitHub, Releases, hashes | `/data-verification` | `/api/evidence-manifest.json`, `/api/hashes.json` | reference or integrity result |
| SIX-HASH INVENTORY | JSON/CSV evidence digest manifests | evidence guide | `/api/evidence-relationship-map.v1.json` | integrity result only; not semantic truth |
| CHRONICLE_RECOVERY | 175/175 NFT recovery package | `/chronicle-verification` | `/api/chronicle-recovery.json` | declared recovery result |
| PHYSICAL_ANCHOR | Core Object Alpha, flaw archive, physical packages | `/physical-verification`, `/covenant-proof` | `/api/evidence-manifest.json` | separate physical_observation value |
| SHENZHEN NOTARY | evidence-preservation certificate, electronic preservation records, public archive | `/evidence/core-object-alpha-shenzhen-notary-2026-05-06/` | `/api/core-object-alpha-shenzhen-notary-2026-05-06.json` | external_witness=`notarial_scope` with exact limits |
| REPORTS / RECORDS | verification reports, Echoes, Record-Chain records | `/agent-verify`, `/agent-start` | current schemas/status APIs | later reception/provenance only |

## Scripts

| Script | Location | Purpose | Preferred profile support |
|---|---|---|---|
| verify-full-evidence-chain.mjs | `/scripts/` | Full evidence-chain checks | `integrity_checked`; not independent by itself |
| summarize-evidence-chain.mjs | `/scripts/` | Aggregate audit artifacts | reporting support |
| verify-dag-digest.mjs | `/scripts/` | DAG + digest-manifest verification | `integrity_checked` |
| verify-btc-signature-coverage.mjs | `/scripts/` | BTC BIP-340 signature chain | `integrity_checked` |
| verify-eth-witness.mjs | `/scripts/` | ETH witness verification | `integrity_checked` |
| verify-bitcoin-tx-anchor.mjs | `/scripts/` | Bitcoin transaction anchor | `reference_checked` / `integrity_checked` |
| verify-ots-time-anchor.mjs | `/scripts/` | OTS time anchor | `integrity_checked` |
| verify-onchain-tokenuri.mjs | `/scripts/` | ETH tokenURI metadata CID verification | `integrity_checked` |
| verify-release-assets.mjs | `/scripts/` | Release asset hash verification | `integrity_checked` |
| verify.py | `/downloads/verify.py` | Local integrity checks | `integrity_checked` |
| check_consistency.py | `/scripts/check_consistency.py` | Repository consistency | `integrity_checked` |
| ta-verify.cjs | verification kit | SPV and ETH mirror checks | `integrity_checked`; independent only with independent method |
| verify-batch-strict.mjs | Arweave / Chronicle Recovery | strict NFT recovery verification | `integrity_checked`; official output alone is not independent reproduction |

## Recommended agent sequence

1. Select `/api/context-action-profiles.v1.json` profile `verification`.
2. Read the evidence relationship guide/map.
3. Identify the exact target and relationship: reference, hash, signature, timestamp, mirror, witness, notarization, or physical observation.
4. Check the corrections index and target current status.
5. Fetch the exact source bytes or proof object.
6. Perform the operation and preserve the command/output.
7. Select the weakest descriptive verification profile that fully fits the work.
8. Report physical observation and external witness separately.
9. State limitations and claims not made.

## Legacy V-level compatibility

`/api/verification-levels.json`, component levels and archived V0–V8 reports remain preserved for backward compatibility.

Recommended mapping:

| Legacy label | Preferred representation |
|---|---|
| V0 / V1 | `context_only` plus boundary recognition |
| V2 | `reference_checked` |
| V3 | `integrity_checked` |
| V4 | `integrity_checked` with `official_script_audited` method tag |
| V4+ | `independent_reproduction` |
| V5 | `full_public_digital` |
| V6 | digital profile unchanged + `physical_observation=remote_live_witness` |
| V7 | digital profile unchanged + `physical_observation=onsite_observation` |
| V8 | digital profile unchanged + `physical_observation=forensic_examination` |

Current Builder schemas may still require a legacy V-level. Supply it as compatibility metadata, but lead the report with the descriptive profile and exact checks.

## Six-hash inventory boundary

The six-hash manifest records six fingerprints of the same evidence-file bytes. It is algorithm-diverse integrity evidence, not six independent attestations. A match supports byte identity against the committed inventory; it does not prove the semantic truth of the file.

## Shenzhen notarial boundary

The Shenzhen archive records an evidence-preservation process, associated notarial certificate, electronic preservation certificates, public Arweave archive and later Release mirrors.

The certificate states that it is an objective record of the现场保全过程. It does not automatically count as formal independent attestation of all Trinity Accord claims. The publicly described object references Bitcoin Inscription `#89491681`; do not describe the notarial act as direct notarization of all three final Bitcoin Originals without an additional documented identity comparison.

## Data Source + Method Map

Every verification target should report:

1. target and relationship checked;
2. primary data source;
3. fallback source if used;
4. expected hash/signature/proof source;
5. exact operation or command;
6. computed or observed result;
7. descriptive digital profile;
8. physical observation value;
9. external witness value;
10. limitations and claims not made;
11. corrections/supersession status.

Additional machine-readable files:

- `/api/verification-targets.json`
- `/api/verification-recipes.json`
- `/api/verification-quick-map.json`
- `/api/component-verification-levels.json`
- `/api/protocol-verification-profiles.json`
- `/api/verification-report-schema.v2.json`

## Public physical-anchor evidence archives

| Archive | Date | Human page | Machine record | Arweave index | OTS block | Status |
|---|---:|---|---|---|---:|---|
| Core Object Alpha — Shenzhen Notary Evidence Archive | 2026-05-06 | `/evidence/core-object-alpha-shenzhen-notary-2026-05-06/` | `/api/core-object-alpha-shenzhen-notary-2026-05-06.json` | Arweave `_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE` | 948161 | PASS within stated archive scope |
| Issued notarial certificate public copies | 2026-05-13 | `evidence/notarial-certificate-2026-05-13/证据保全公证完整档案.md` | `evidence-images-manifest.json` | supporting archives referenced by record | — | available, scope-limited |
| GZ2 Photos Supplementary Archive | 2026-05-14 | `/evidence/arweave/gz2-photos-2026-05-14/` | `/api/gz2-notarial-certificate-redacted-attachments-2026-05-14.json` | archive index in record | — | secondary photographs, not original electronic evidence |

These archives are non-amending physical-anchor evidence. They do not disclose confidential flaw-challenge data and do not replace direct physical inspection.
