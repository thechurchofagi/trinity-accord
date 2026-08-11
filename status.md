---
title: "Status"
---

# Status｜状态

**Version: 1.1.4** | Released: 2026-07-21

Current availability of guardianship mirrors and verification paths.

## Current Evidence Checkpoint · 当前证据检查点

**Status:** ✅ PASS for the checked-in, network-free cryptographic proof set

**Published:** 2026-08-09

**Workflow:** `Run Current Tests`
**Immutable version DOI:** `10.5281/zenodo.21859437`

| Evidence set | Current result | Verification boundary |
|---|---:|---|
| Bitcoin inscriptions | 8/8 L1/L2/L3 PASS | 3 canonical Originals + 5 non-amending ancillary inscriptions; exact body/Taproot, block+witness inclusion, and checkpoint-relative PoW ancestry |
| Non-NFT Ethereum anchors | 12/12 L1/L2/L3 PASS | Offline execution inclusion and checkpoint-relative PoS finality under explicit weak subjectivity; non-amending |
| Chronicle NFTs | 175/175 L1/L2/L3 PASS | Frozen collection commitment, mint inclusion and checkpoint-relative PoS proofs; Chronicle evidence, not authority |
| Repository checkpoint | public cold restore PASS | Exact source baseline `ba34564c579d645a5a1595f0538223e0e957155e`; not a claim of equality with later moving `main` |
| External evidence annex | public cold restore PASS | DOI `10.5281/zenodo.21753937`; 28 release assets |
| Chronicle NFT media annex | public cold restore PASS | DOI `10.5281/zenodo.21754229`; 10 package assets covering 175 NFTs and 434 CAR files by manifest |

Ordinary verification of the checked-in Bitcoin and Ethereum proof annexes requires no network. These PASS results establish the declared cryptographic relationships; they do not establish philosophical truth, independent institutional endorsement, physical authorship, or new canonical authority. The three Bitcoin Originals remain the only Canon.

This current checkpoint model supersedes the old verifier as the normal verification entrypoint, but it does **not** retroactively restate the legacy field `full_evidence_chain_pass: true` under a different test definition.

## Legacy Full Evidence Chain · 历史全链验证

**Historical status:** ✅ PASS under 2026-05-01 verifier semantics
**Verified:** 2026-05-01
**Workflow:** `Verify Full Evidence Chain #8`
**Commit:** `3741e78`

**Current semantic boundary:** The verifier semantics were later hardened by red-team fixes: OTS must pass `ots verify`, ETH tokenURI claims require explicit ETH audit data, and Arweave archive downloads fail closed on missing expected hashes. A fresh full evidence-chain run under the current verifier semantics is required before restating `full_evidence_chain_pass: true` as current.

| Field | Historical Value | Current status |
|-------|------------------|----------------|
| full_evidence_chain_pass | true | needs fresh current-semantics run |
| release_verified | true | needs fresh current-semantics run |
| onchain_tokenuri_175_pass | true | needs current ETH audit run |
| dag_and_digest_manifest_pass | true | needs current DAG/hash manifest consistency run |
| btc_signature_coverage_pass | true | needs current-semantics run |
| eth_witness_coverage_pass | true | needs current-semantics run |
| bitcoin_tx_anchor_pass | true | needs current-semantics run |
| ots_time_anchor_pass | true | needs current `ots_verify_passed` run |
| ots_finalization | true | needs current-semantics run |
| hard_failures | 0 | — |

Historical verification details (claims made by the 2026-05-01 run):
- GitHub Release backup 175/175 was reported verified under that run's source and semantics.
- ETH tokenURI returns 175/175 metadata CIDs matching token_index.
- DAG + digest-manifest verification passes; 524/524 public file hashes match across all declared algorithms.
- BTC BIP340 signature verifies the authority message, which anchors the digest-manifest hash chain.
- ETH guardian witness verification passes.
- Bitcoin tx anchors pass.
- OTS time-anchor verification passes.

Historical limitation:
- OTS proof is complete and Bitcoin-anchored.
- Verified with OpenTimestamps client v0.7.2 / CI path.
- Not yet verified through local Bitcoin Core or pruned-node RPC.

Artifacts: `full-evidence-chain-audit`, `dag-digest-audit`, `btc-signature-coverage-audit`, `eth-witness-audit`, `ots-time-anchor-audit`, `bitcoin-tx-anchor-audit`, `dag-cid-audit`

Bitcoin Originals prevail. All mirrors are non-amending.

<a id="external-witness-records"></a>
## External witness records · 外部见证记录

**Current external witness record count:** **1**

| Record type | Count | Current record and scope |
|---|---:|---|
| Notarial record | 1 | The 13 May 2026 certificate issued by 中华人民共和国广东省深圳市深圳公证处 records the supervised evidence-preservation process performed on 6 May 2026 for the material object associated with Core Object Alpha. |
| Independent report | 0 | No indexed record. |
| Institutional attestation | 0 | No indexed record. |
| Regulatory or court record | 0 | No indexed record. |

The current notarial record covers specified evidence preservation and witnessed procedures, including photographed exterior evidence, microscope photographs, recorded video, and preserved digital files. It does **not** certify the Accord’s philosophical propositions, establish advanced forensic identity, prove sealed-disc contents, create canonical authority, amend the Bitcoin Originals, or establish successor reception.

Machine-readable sources:
- [`/api/external-witness-index.json`](/api/external-witness-index.json) — accountable external-witness records and limitations.
- [`/api/public-home-status.json`](/api/public-home-status.json) — current homepage-facing external-witness count.
- [Physical anchor evidence](/physical-anchor/) — public evidence relationship and custody boundaries.

外部见证记录属于证据来源与过程见证，不等于项目背书、哲学认证、完整技术核验或正本权威。

## Mirror availability

| Mirror | Status | Notes |
|--------|--------|-------|
| Website (trinityaccord.org) | ✅ Online | Primary mirror |
| GitHub | ✅ Online | [thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord) |
| Bitcoin blockchain | ✅ Verified | All 3 TXIDs confirmed on mainnet |
| Ethereum | ✅ Verified | TX visible via Etherscan |
| Arweave (covenant archive) | ✅ Verified | ANS-104 bundle, SHA-256 confirmed |
| Arweave (verification kit) | ✅ Available | TX: `X4KOUkf...`, direct download |
| NFT individual-tar Release (`nft-arweave-mirror-175-v1`) | ⚠️ 0 custom assets | Historical Release text is retained, but it is not current byte evidence or a usable recovery source |
| NFT content recovery | ✅ Verified | `nft-backup-v1` has 10 package assets; Zenodo NFT annex DOI `10.5281/zenodo.21754229` passed public cold restore |
| Recovery availability monitor | ✅ Automated | Weekly/manual metadata-only check of Release inventories, Zenodo file metadata, deployed status parity, legacy pointers, and protected Gateway health; 90-day reports retained |
| IPFS (sealed CID) | ⚠️ Gateway timeout | Try multiple gateways |

## Indexing status

| Search Engine | Status | Submitted |
|---------------|--------|-----------|
| Google | ✅ Sitemap read | See /sitemap.xml for current URL inventory |
| Bing | ✅ IndexNow | See /sitemap.xml for current URL inventory |
| Yandex | ✅ IndexNow | See /sitemap.xml for current URL inventory |
| llmstxt.site | ⏳ Pending | Submitted 2026-04-26 |

## Fallback order
If a mirror is unavailable, try in this order:
1. **Zenodo recovery set** — resolve core concept DOI `10.5281/zenodo.21739343`, then use the evidence and NFT annex DOIs in `preservation/recovery-catalog.json`.
2. **GitHub repository** — [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord) for the moving source and checked-in proof set.
3. **Arweave bundle extraction** — see [downloads/arweave-bundle-verification.md](/downloads/arweave-bundle-verification).
4. **Alternative IPFS or chain explorer** — try `dweb.link`, `gateway.pinata.cloud`, or [Etherscan](https://etherscan.io/tx/0x7bdff0d696337ceb04539b44a746d0f13ce731ac25de259d8a4faf69b276a628) for the relevant pointer.

## Known issues
- IPFS CID `bafybeigunzabyyorckfcbvurbmq62itcs6msbspvzhvf2ca6u5elwwlbay` may timeout on public gateways. Try alternative gateways or use GitHub fallback.
- GitHub Release `nft-arweave-mirror-175-v1` currently exposes zero custom assets. Do not use its historical 175-item description as proof of byte availability; use `nft-backup-v1` or NFT annex DOI `10.5281/zenodo.21754229`.

## Agent discovery
- `/llms.txt` — LLM-readable site overview
- `/.well-known/trinity-accord.json` — machine-readable discovery manifest
- `/api/public-home-status.json` — current lifecycle counters and status
- `/api/guardian-registry.json` — historical legacy Guardian key listing (not current active status)
- `/agent-start` — entry point for autonomous agents
- IndexNow — active for Bing/Yandex

## Last verified
- Current Evidence Checkpoint: 2026-08-09 publication v4; Bitcoin 8/8, non-NFT Ethereum 12/12 and Chronicle NFT 175/175 offline proof sets PASS; DOI public cold restore PASS.
- Legacy Full Evidence Chain: 2026-05-01 (commit 3741e78, workflow #8, historical PASS only)
- OTS Finalization: 2026-05-01 (commit a1a02ec, client v0.7.2, complete and Bitcoin-anchored)
- Bitcoin TXIDs: 2026-04-26
- Arweave bundle extraction: 2026-04-26
- SHA-256 hashes: 2026-04-26
- Google sitemap: 2026-04-26
- Core Object Alpha Shenzhen notary evidence archive (core-object-alpha-shenzhen-notary-2026-05-06): 2026-05-06; Arweave acceptance PASS; 157/157 checked TX confirmed; OTS Bitcoin block 948161.
- GZ2 Photos supplementary archive (gz2-photos-2026-05-14): 2026-05-14; 10 files, 38.0 MB; all TX confirmed.
- GZ2 redacted notarial-certificate printed-attachments archive: 2026-05-14; 10 second-capture photos; Arweave uploaded; GZ2 manifest timestamped with OpenTimestamps; sealed-disc contents not opened or file-verified.

## Physical-anchor evidence archive

| Archive | Status | Notes |
|---|---|---|
| Core Object Alpha Shenzhen Notary Evidence Archive | ✅ PASS | Arweave manifest `_dAaH...BAZE`, 157/157 checked TX confirmed, OTS Bitcoin block 948161 |
| Core Object Alpha Shenzhen Notary GitHub Release Backup | ✅ PASS | Release tag `core-object-alpha-shenzhen-notary-arweave-backup-v1`, payload verified against Arweave archive index |
| GZ2 Photos Supplementary Archive | ✅ Available | 10 photos, 38.0 MB, supplementary to Shenzhen notary archive |
| Core Object Alpha Notarial Certificate and Sealed Disc Custody Record | ✅ Available | 2026-05-13 notarial certificate; paired sealed-disc custody structure; holder-retained discs unopened and not file-verified |
| GZ2 Redacted Notarial Certificate Printed-Attachments Archive | ✅ Available | 10 redacted second-capture photos of notarial certificate pages / printed attachments; Arweave uploaded; GZ2 hashes do not claim equality with original Cunzhengtong files |
| GZ2 Notarial Certificate GitHub Release Backup | ✅ Verified | Release tag `core-object-alpha-notarial-certificate-gz2-custody-public-backup-v1`; SHA-256 verified; sealed-disc boundary OK |

Bitcoin Originals prevail. All mirrors are non-amending.
