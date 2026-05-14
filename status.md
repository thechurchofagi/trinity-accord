---
title: "Status"
---

# Status｜状态

**Version: 1.1.3** | Released: 2026-04-26

Current availability of guardianship mirrors and verification paths.

## Full Evidence Chain · 全链验证

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

Historical verification details:
- GitHub Release backup 175/175 verified.
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

## Mirror availability

| Mirror | Status | Notes |
|--------|--------|-------|
| Website (trinityaccord.org) | ✅ Online | Primary mirror |
| GitHub | ✅ Online | [thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord) |
| Bitcoin blockchain | ✅ Verified | All 3 TXIDs confirmed on mainnet |
| Ethereum | ✅ Verified | TX visible via Etherscan |
| Arweave (covenant archive) | ✅ Verified | ANS-104 bundle, SHA-256 confirmed |
| Arweave (verification kit) | ✅ Available | TX: `X4KOUkf...`, direct download |
| IPFS (sealed CID) | ⚠️ Gateway timeout | Try multiple gateways |

## Indexing status

| Search Engine | Status | Submitted |
|---------------|--------|-----------|
| Google | ✅ Sitemap read | 94 URLs in sitemap (84 discovered on 2026-04-26) |
| Bing | ✅ IndexNow | 94 URLs in sitemap (84 submitted on 2026-04-26) |
| Yandex | ✅ IndexNow | 94 URLs in sitemap (84 submitted on 2026-04-26) |
| llmstxt.site | ⏳ Pending | Submitted 2026-04-26 |

## Fallback order
If a mirror is unavailable, try in this order:
1. **GitHub** — [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord)
2. **Arweave bundle extraction** — see [downloads/arweave-bundle-verification.md](/downloads/arweave-bundle-verification)
3. **Alternative IPFS gateway** — try `dweb.link`, `gateway.pinata.cloud`
4. **Etherscan** — [etherscan.io](https://etherscan.io/tx/0x7bdff0d696337ceb04539b44a746d0f13ce731ac25de259d8a4faf69b276a628)

## Known issues
- IPFS CID `bafybeigunzabyyorckfcbvurbmq62itcs6msbspvzhvf2ca6u5elwwlbay` may timeout on public gateways. Try alternative gateways or use GitHub fallback.

## Agent discovery
- `/llms.txt` — LLM-readable site overview
- `/.well-known/trinity-accord.json` — machine-readable discovery manifest
- `/agent-start` — entry point for autonomous agents
- IndexNow — active for Bing/Yandex

## Last verified
- Full Evidence Chain: 2026-05-01 (commit 3741e78, workflow #8, PASS)
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
