# Verify｜验证中心

This page defines verification levels L0-L5.

- Highest verification standard: **L5**
- Strongest remote standard: **L3**
- Minimum serious digital standard: **L1-L2**

## L0 — Recognition / 识别级
Goal: Identify the Accord and authority boundary.
Pass: can state Accord scope, Bitcoin Originals final authority, mirrors non-amending.

## L1 — Canonical Bitcoin Verification / 比特币本体验证级
Goal: verify three inscriptions, TXIDs, and shared authority address.
Pass: confirm inscriptions 97631551/98369145/98387475, listed TXIDs, and authority address.

**How to verify:**
- Use any of these block explorers (if one is blocked, try another):
  - ordinals.com: `/inscription/{ID}`
  - ordiscan.com: `/inscription/{ID}`
  - mempool.space API: `/api/tx/{TXID}` (returns JSON, no browser needed)
- Confirm all three TXIDs exist on Bitcoin mainnet.
- Confirm the output address matches the authority address.

## L2 — Mirror Integrity Verification / 镜像完整性验证级
Goal: verify mirror manifests, hashes, pointers.
Pass: fetch `/api/authority.json` + `/api/evidence-manifest.json`, verify listed hashes/pointers, keep non-amending boundary.

**How to verify:**
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
