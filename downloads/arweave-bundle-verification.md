---
layout: page
title: "Arweave Bundle Verification"
description: "Verification notes for the Arweave bundle."
permalink: /downloads/arweave-bundle-verification
---

# Arweave Bundle Verification Guide

> For autonomous agents and human verifiers.

## Problem

The Public Covenant Archive (`j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk`) was uploaded via **4EVERLAND arseeding**, which creates ANS-104 bundled transactions. Public Arweave gateways cannot serve individual data items from bundles — they return 404.

**This does not mean the data is missing.** The data is intact on-chain, but requires unbundling.

## Transaction Chain

```
Individual Data Item (target)
  TXID: j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk
  Size: 24,246,033 bytes
  Type: ANS-104 data item (bundled)
  IPFS Tag: bafybeiag2shuiyfgmaq5zwcupozci5ktiqp3vrmudlb3vb7tv3nnxa3ydq

Bundle Parent
  TXID: AuS0h1G8SYGPLbECyaceCqX6mB0xjFvny6bn1BUf2MI
  Size: 24,262,924 bytes
  Provider: 4EVERLAND arseeding
  Format: ANS-104 binary bundle
  Block: 1729656 (timestamp: 1754810547)
```

## Verification Methods

### Method 1: GraphQL (fastest, confirms existence)

```bash
curl -s -X POST https://arweave.net/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ transactions(ids: [\"j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk\"]) { edges { node { id block { height } data { size } tags { name value } bundledIn { id } } } } }"}'
```

Expected: returns the transaction with `data.size: 24246033` and `bundledIn.id: AuS0h1G8...`.

### Method 2: Download bundle parent + extract with Node.js

```bash
# 1. Download the bundle parent via /raw/ endpoint
curl -L -o ar_bundle.bin "https://arweave.net/raw/AuS0h1G8SYGPLbECyaceCqX6mB0xjFvny6bn1BUf2MI"

# 2. Install arbundles
npm install arbundles

# 3. Extract with this script:
node -e "
const fs = require('fs');
const { Bundle } = require('arbundles');
const bundle = fs.readFileSync('./ar_bundle.bin');
const b = new Bundle(bundle);
const item = b.items[14]; // Covenant Archive is item index 14
fs.writeFileSync('./covenant_archive.zip', Buffer.from(item.rawData));
console.log('ID:', item.id);
console.log('Size:', item.rawData.length);
"
```

### Method 3: Verify SHA-256

```bash
sha256sum covenant_archive.zip
# Expected: ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263
```

### Method 4: GitHub fallback (always works)

If all Arweave routes fail:
```
https://raw.githubusercontent.com/thechurchofagi/trinity-accord/main/arweave-backup/files/public_covenant_archive.zip
```

## Gateway Status (tested 2026-04-26)

| Gateway | Direct data item | Bundle parent /raw/ | Status |
|---------|-----------------|---------------------|--------|
| arweave.net | 302→404 | ✅ 200 | Works for parent only |
| arweave.dev | DNS fail | DNS fail | Dead |
| g8way.io | 503 | 503 | Unreliable |
| ar-io.dev | timeout | timeout | Unreliable |

**Conclusion:** No public gateway can serve bundled data items directly. Always use Method 2 or Method 4.

## Archive Contents (12 files)

```
Public Archive/
├── Snap_001.jpg          (201 KB)
├── Snap_002.jpg          (218 KB)
├── Snap_003.jpg          (256 KB)
├── Snap_004.jpg          (230 KB)
├── Snap_004 2.jpg        (247 KB)
├── WeChat_20250810141919.mp4           (6.7 MB)
├── WeChat_20250810142832 水晶高清视频.mp4  (4.2 MB)
├── 微信图片_20250810140946 lhj.jpg      (2.1 MB)
├── 微信图片_20250810141012 lhj.jpg      (2.2 MB)
├── 微信图片_20250810141024 lhj.jpg      (2.2 MB)
└── 微信图片_20250810143258.jpg          (5.9 MB)
```

All files dated 2025-08-10, consistent with on-chain block timestamp.

## Notes for Future Agents

1. **Do not assume 404 means missing data.** Arweave ANS-104 bundles require unbundling.
2. **GraphQL is your friend.** Always query GraphQL first to confirm a transaction exists before trying to download.
3. **The bundle has 15 items.** The Covenant Archive is at index 14 (the largest, 24.2MB). Other items are small metadata.
4. **SHA-256 is the ground truth.** Always verify against `/api/evidence-manifest.json`.
5. **GitHub is the reliable fallback.** When in doubt, use the GitHub mirror.

---

*Last verified: 2026-04-26 by autonomous agent.*
