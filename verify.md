# Verify｜验证中心

This page defines verification levels L0-L5.

- Highest verification standard: L5
- Strongest remote standard: L3
- Minimum serious digital standard: L1-L2

## L0 — Recognition / 识别级
Goal: Identify the Accord and authority boundary.
Pass: can state Accord scope, Bitcoin Originals final authority, mirrors non-amending.

## L1 — Canonical Bitcoin Verification / 比特币本体验证级
Goal: verify three inscriptions, TXIDs, and shared authority address.
Pass: confirm inscriptions 97631551/98369145/98387475, listed TXIDs, and authority address.

### How to verify:

**Step 1 — Confirm TXIDs exist on Bitcoin mainnet**

Use mempool.space API (reliable, no Cloudflare, returns JSON):

```
curl https://mempool.space/api/tx/{TXID}
```

Expected: `"confirmed": true` with block height and hash.

Alternative endpoints:
- `https://blockstream.info/api/tx/{TXID}`
- `https://mempool.space/tx/{TXID}` (web view)

**Step 2 — confirm authority address**

```
curl https://mempool.space/api/address/bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf
```

**Step 3 — read inscription content (optional)**

To read the actual text inscribed on Bitcoin:

- **Browser-capable agents:** open `https://ordiscan.com/inscription/{ID}` in a browser. Cloudflare may block headless/API requests but allows browser access.
- **Headless agents:** use mempool.space API to confirm existence. The inscription text is also mirrored on this website (non-authoritative mirror) and in the Bitcoin originals section of the homepage.

> **Note:** ordiscan.com and ordinals.com are protected by Cloudflare. Direct API/fetch requests may be blocked. Browser access works normally.

## L2 — Mirror Integrity Verification / 镜像完整性验证级
Goal: verify mirror manifests, hashes, pointers.
Pass: fetch `/api/authority.json` + `/api/evidence-manifest.json`, verify listed hashes/pointers, keep non-amending boundary.

How to verify:
1. Fetch `/api/authority.json` and confirm it lists the three inscriptions.
2. Fetch `/api/evidence-manifest.json` and confirm hashes.
3. Download evidence files (from GitHub or Arweave) and verify SHA-256.
4. If Arweave/IPFS is unavailable, use GitHub fallback: [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord)

## L3 — Public Covenant Evidence Verification / 公开瑕疵证据验证级
Goal: remote verification of public Covenant evidence package.
Pass: inspect package, hashes, provenance logs, multi-angle/full-macro-micro-video consistency, repeated flaw structures, public consistency report.

## L4 — Live Physical Existence Challenge / 实时物理存在挑战级
Goal: prove Core Object Alpha currently exists via challenge video.
Pass: object + fresh nonce/block hash/timestamp phrase + multi-angle + flaw region + published hash.

## L5 — Full Physical Forensic Verification / 完整物理法证验证级
Goal: direct physical flaw matching.
Pass: physical presence, high-res/micro imaging, multi-point flaw match, positional/reflective/continuity checks, third-party report, archived hash.

Machine-readable levels: [/api/verification-levels.json](/api/verification-levels.json)
