# Status｜状态

**Version: 1.1.1** | Released: 2026-04-26

Current availability of guardianship mirrors and verification paths.

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
- Bitcoin TXIDs: 2026-04-26
- Arweave bundle extraction: 2026-04-26
- SHA-256 hashes: 2026-04-26
- Google sitemap: 2026-04-26

Bitcoin Originals prevail. All mirrors are non-amending.
