---
layout: default
title: "Evidence Mirror Status"
description: "Status of evidence mirrors for The Trinity Accord."
---

# Trinity Accord — Evidence Mirror Status

## Final Status Summary

```
NFT Release mirror: PASS
Full Evidence Chain: PASS
OTS finalization: PASS

Flaw Covenant video Arweave mirror: Verified
Flaw Covenant video GitHub Release mirror: PASS
OTS proof bundle Arweave mirror: Verified
OTS proof bundle GitHub Release mirror: PASS

Remaining limitation:
OTS has not yet been verified through local Bitcoin Core / pruned-node RPC.
```

## Evidence Mirror Layers

### Flaw Covenant Videos

- Arweave raw mirror: Verified
- GitHub Release mirror: PASS
- Release: flaw-covenant-video-mirror-v1
- Assets: 5/5

The video SHA-256 digests were prior Bitcoin / OTS anchored. The Arweave uploads are new raw availability mirrors of already-anchored files. The GitHub Release is a verified mirror of the Arweave payloads.

### OTS Proof Bundle

- Arweave bundle mirror: Verified
- GitHub Release mirror: PASS
- Release: ots-proof-bundle-mirror-v1
- Assets: 4/4

The OTS proof bundle is now mirrored on Arweave and GitHub Release. The Arweave payload was verified by SHA-256 and size. The GitHub Release assets were downloaded back and verified. The internal OTS bundle checksums passed.

This strengthens long-term availability of OTS proof artifacts, but does not by itself constitute local Bitcoin Core / pruned-node independent OTS verification.

The bundle preserves OTS proof artifacts and related verification records. Client-level OTS verification still requires the original timestamped files, including digest-manifest.json / digest-manifest.csv, from the repository or another verified mirror.

## Boundary

All GitHub Releases listed here are verified availability mirrors. They are not canonical authority. They are not evidence amendments. They do not replace Bitcoin / OTS / digest-manifest evidence.
