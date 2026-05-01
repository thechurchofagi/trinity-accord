# Status｜状态

**Version: 1.1.2** | Released: 2026-04-26

Current availability of guardianship mirrors and verification paths.

## Full Evidence Chain · 全链验证

**Status: ✅ PASS** | Verified: 2026-05-01 | Workflow: `Verify Full Evidence Chain #8` | Commit: `3741e78` | Duration: 34s | Artifacts: 7/7 uploaded | hard_failures: 0

| Field | Value |
|-------|-------|
| full_evidence_chain_pass | true |
| release_verified | true |
| onchain_tokenuri_175_pass | true |
| dag_and_digest_manifest_pass | true |
| btc_signature_coverage_pass | true |
| eth_witness_coverage_pass | true |
| bitcoin_tx_anchor_pass | true |
| ots_time_anchor_pass | true |
| ots_finalization | true |
| ots_upgrade_mutation | none |
| ots_digest_manifest_mutation | none |
| hard_failures | 0 |

What this verifies:
- GitHub Release backup 175/175 verified.
- ETH tokenURI returns 175/175 metadata CIDs matching token_index.
- DAG + digest-manifest verification passes; 524/524 public file hashes match across all declared algorithms.
- BTC BIP340 signature verifies the authority message, which anchors the digest-manifest hash chain.
- ETH guardian witness verification passes.
- Bitcoin tx anchors pass.
- OTS time-anchor verification passes.

Limitation:
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
| Google | ✅ Sitemap read | 23 URLs discovered |
| Bing | ✅ IndexNow | 23 URLs submitted |
| Yandex | ✅ IndexNow | 23 URLs submitted |
| llmstxt.site | ⏳ Pending | Submitted 2026-04-26 |

## Fallback order
If a mirror is unavailable, try in this order:
1. **GitHub** — [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord)
2. **Arweave bundle extraction** — see [downloads/arweave-bundle-verification.md](/downloads/arweave-bundle-verification.md)
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

Bitcoin Originals prevail. All mirrors are non-amending.
