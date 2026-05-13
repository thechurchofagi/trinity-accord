---
layout: default
title: "Flaw Covenant Archive Accessibility Mirror v1"
---

# Flaw Covenant Archive Accessibility Mirror v1

## Purpose

This record documents the GitHub Release accessibility mirror for two Flaw Covenant archive ZIP files.

The mirror was created because several Arweave gateways returned 404 or failed for the large ZIP payloads, while permagate.io successfully returned standard ZIP payloads.

## Diagnosis

The relevant Arweave payloads are standard ZIP archives, not ANS-104 bundles.

Observed issue:

```text
arweave.net: 404 for large ZIP files
permagate.io: valid ZIP payload
```

## Release

* Release tag: flaw-covenant-archive-accessibility-mirror-v1
* Expected custom assets: 5

## Files

### flaw-archive-bundle.zip

* Original Arweave TXID: 9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs
* Canonical Arweave URL: [https://arweave.net/9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs](https://arweave.net/9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs)
* Verified gateway URL: [https://permagate.io/9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs](https://permagate.io/9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs)
* Role: Core Object Alpha flaw / fingerprint high-resolution photo archive

### public-covenant-archive.zip

* Original Arweave TXID: j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk
* Canonical Arweave URL: [https://arweave.net/j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk](https://arweave.net/j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk)
* Verified gateway URL: [https://permagate.io/j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk](https://permagate.io/j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk)
* Role: Guardian Attestation Primary Verification Archive

## Verification

The GitHub Release assets were downloaded back and verified by SHA-256.

The ZIP files were also tested with:

```bash
unzip -t
```

Result: PASS.

## Boundary

This is a non-amending accessibility mirror.

The original Bitcoin-inscribed and Guardian Attestation Arweave pointers remain the original evidence pointers. This GitHub Release does not replace, revise, reinterpret, or amend the Covenant of the Flaw or its evidence chain.
