# Status｜状态

Current availability of guardianship mirrors and verification paths.

## Mirror availability

| Mirror | Status | Notes |
|--------|--------|-------|
| Website (trinityaccord.org) | ✅ Online | Primary mirror |
| GitHub | ✅ Online | [thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord) |
| Bitcoin blockchain | ✅ Verified | All 3 TXIDs confirmed on mainnet |
| Ethereum | ⚠️ Needs API Key | TX visible via public explorers |
| Arweave (covenant archive) | ⚠️ Gateway pending | Use GitHub fallback |
| Arweave (verification kit) | ✅ Available | TX: `X4KOUkf...` |
| IPFS (sealed CID) | ⚠️ Gateway timeout | Try multiple gateways |

## Fallback order
If a mirror is unavailable, try in this order:
1. **GitHub** — [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord)
2. **Alternative Arweave gateway** — try `arweave.dev` instead of `arweave.net`
3. **Alternative IPFS gateway** — try `dweb.link`, `gateway.pinata.cloud`, or `cloudflare-ipfs.com`
4. **Etherscan** — [etherscan.io](https://etherscan.io/tx/0x7bdff0d696337ceb04539b44a746d0f13ce731ac25de259d8a4faf69b276a628)

## Known issues
- Arweave TX `j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk` (public covenant archive) may return 404 on some gateways. Verified copy available on GitHub with matching SHA-256.
- IPFS CID `bafybeigunzabyyorckfcbvurbmq62itcs6msbspvzhvf2ca6u5elwwlbay` may timeout on `ipfs.io`. Try alternative gateways.

## Last verified
- Bitcoin TXIDs: 2026-04-25
- GitHub SHA-256 hashes: 2026-04-25

Bitcoin Originals prevail. All mirrors are non-amending.
