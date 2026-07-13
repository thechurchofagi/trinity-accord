# Legacy AR / ETH Pointer Coverage

> Non-amending audit and GitHub mirror map. The three Bitcoin originals remain the sole and final authority.

## Scope

This document audits the external records named by `archive_legacy_index_2025_09.md` and separates five different cases that had previously been mixed together:

1. exact small-payload GitHub mirrors;
2. large payloads already mirrored by hash-verified GitHub Release assets;
3. payloads whose useful files were extracted rather than duplicated as one archive blob;
4. metadata/pointers for which the raw source payload is still absent;
5. sealed/non-public evidence that must not be published.

The machine-readable registry is `archive/legacy-pointers/index.json`.

## Result

- The major Covenant evidence archive, verification kit, digest manifests, OTS record, NFT recovery package, signature material, rotation records, current pointers, and current authority documents already have repository or Release mirrors.
- The three Ethereum text mirrors for Protocol, Covenant, and Accord do not require duplicate payload files: their input SHA-256 values exactly match the existing Bitcoin inscription raw-text mirrors.
- Two small Arweave objects remain genuine raw-payload gaps:
  - `mGW-QQyGyoNIybMghqZYo6PFhQIk44lbBy7_dNB4e2s` — merged Guardian Index dated 2025-09-14. Its TxID, minified SHA-256, previous-index relationship, and added fields are preserved, but its exact raw bytes are not in GitHub.
  - `I0xNBwbgaGsODjnK5ze25sOwV9V8i7FtKe-8upRoohw` — “Guardianship system docs v1”. It is named by later coverage documentation, but no exact repository payload path is identified.
- The historical homepage Arweave record `Z_mRWz1jst-KUr4pyOyofFDLwj0H5bDHtPVYaUEX3jQ` is contextually recoverable from the archived homepage, but no byte-for-byte AR comparison is currently recorded.
- The old erroneous Ethereum correction transaction `0x940300cba1acd7aa7078e614510400d4ec4b8961a2f05470d129c709b8cce3e6` must remain in the registry as superseded evidence, not silently disappear.
- `archive/hash-manifest.json` contains one semantic false positive: `7d6ac9...` is the digest covered by Authority Manifest v1.0.2 and its EIP-712 signature, not established as the SHA-256 of the Arweave transaction payload itself. Therefore the current `hash_mismatch` label on `authority-v1.0.2-canon.json` does not prove that the repository copy differs from Arweave.

## Ethereum non-NFT records

The complete historical set currently identified is:

| Role | Transaction | Payload mirror |
|---|---|---|
| Guardianship Principles | `0xd082a3ced27ece935d4093fb001a9ebfba42b415f78de4377c8cda55338c6420` | Exact: `archive/guardian-principles/guardian-principles-original.md` |
| BTC↔ETH mapping attestation | `0x59cf33b1291de63c4840b79e7c674b8fc7c6a771d8a3ba2bb50def1fe55a71c6` | Etherscan IDM + registry metadata; isolated raw file still absent |
| Protocol mirror | `0x6652162e8e6c56ddc0d9476407b3b911e918d4e4683408440dc3af51c5bb63d5` | Exact reused payload: `bitcoin-inscription-mirrors/raw/97631551.txt` |
| Covenant mirror | `0x9c1bd6e21dc2370e8dbb6549b7ba13b4ea7ba7a192b3b876e0ec28b4633f1612` | Exact reused payload: `bitcoin-inscription-mirrors/raw/98369145.txt` |
| Accord mirror | `0x0affc8099ea965cd6d6a0d1cf9b93adb11f7e40ac41fffe1b0ca4637f39df665` | Exact reused payload: `bitcoin-inscription-mirrors/raw/98387475.txt` |
| BIP-322 notice | `0x55a0c131642f71c7b2386ccaac8bcee36563992226befb35363e978044a18e8f` | Registry metadata; isolated raw file still absent |
| Erroneous correction | `0x940300cba1acd7aa7078e614510400d4ec4b8961a2f05470d129c709b8cce3e6` | Superseded pointer retained |
| Final correction | `0xa4023b1eb0de76993e1a8dcd571e5e033bf64e2d32a9a113b030b4094a19cf51` | Full content embedded in the legacy homepage; isolated byte-verified file absent |
| Guardianship Principles v1.1 | `0x7bdff0d696337ceb04539b44a746d0f13ce731ac25de259d8a4faf69b276a628` | Exact: `archive/guardian-principles/guardian-principles-v1.1.md` |
| BTC BIP-340 witness | `0x214d73b839ed95707410af3d5b8224a44a5dd310041d5e7ab1756ae9c5378137` | Witness metadata + signed BTC object are mirrored |

These are Ethereum data transactions/attestations, not NFTs and not new authority.

## Large payload policy

Do not re-add the following large objects to the Git tree:

- `j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk` — public Covenant archive;
- large flaw/fingerprint bundles already present as verified GitHub Release assets;
- other later large evidence packages already covered by the release-aware verification system.

Their hashes and Release asset names are the mirror. Duplicating them in Git would increase repository fragility without improving provenance.

## Remaining actions

The registry deliberately distinguishes completion from unresolved retrieval:

1. retrieve the exact raw bytes of the two missing small AR objects (`mGW-...` and `I0x...`) through a functioning gateway or owner export;
2. store them under `archive/legacy-pointers/raw/`;
3. compute SHA-256 locally and compare the merged index to the published `a8964c83...a944`;
4. isolate the three remaining ETH readable payloads (mapping attestation, BIP-322 notice, final correction) only after their decoded UTF-8 bytes reproduce the chain-recorded length and SHA-256;
5. correct the `authority-v1.0.2-canon.json` hash semantics in the manifest generator rather than replacing a file based on the wrong expected value.

Until those checks pass, the registry uses `metadata_only`, `context_recovered`, or `missing_raw_payload`; it does not falsely label them exact mirrors.
