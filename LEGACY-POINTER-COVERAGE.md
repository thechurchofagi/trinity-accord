# Legacy AR / ETH Pointer Coverage

> Non-amending audit and GitHub mirror map. The three Bitcoin originals remain the sole and final authority.

## Scope

This document audits the external records named by `archive_legacy_index_2025_09.md` and separates five cases that had previously been mixed together:

1. exact small-payload GitHub mirrors;
2. large payloads already mirrored by hash-verified GitHub Release assets;
3. payloads whose useful files were extracted rather than duplicated as one archive blob;
4. context or metadata records that are preserved but not yet compared byte-for-byte with the named external object;
5. sealed/non-public evidence that must not be published.

The machine-readable registry is `archive/legacy-pointers/index.json`.

## Completed result

- Audited **35 Arweave records**, **10 Ethereum non-NFT records**, and the relevant IPFS pointers named by the legacy homepage.
- The major Covenant archive, verification kit, digest manifests, OTS record, NFT recovery package, signature material, rotation records, pointer indexes, and authority documents already had repository or Release coverage.
- The two previously missing small Arweave payloads have now been retrieved and mirrored exactly:
  - `mGW-QQyGyoNIybMghqZYo6PFhQIk44lbBy7_dNB4e2s` — merged Guardian Index, 2,783 bytes, SHA-256 `a8964c83b7ef9801a367115bc71f3be136a8c16a4064e4b9b593aebe66f8a944`.
  - `I0xNBwbgaGsODjnK5ze25sOwV9V8i7FtKe-8upRoohw` — Guardianship system documentation tar payload, SHA-256 `704b70ed311d4fbd39f898f722e98f3be616970d67eccb68a159481402113d12`.
- Their exact bytes are under `archive/legacy-pointers/raw/`, with hashes in `archive/legacy-pointers/raw/SHA256SUMS`.
- Four Ethereum calldata objects that previously lacked isolated raw files have also been retrieved from Ethereum mainnet and mirrored under `archive/legacy-pointers/eth-raw/`.
- The three Ethereum text mirrors for Protocol, Covenant, and Accord are not duplicated: their calldata length and SHA-256 exactly match the existing Bitcoin inscription raw-text mirrors.
- The historical homepage Arweave record `Z_mRWz1jst-KUr4pyOyofFDLwj0H5bDHtPVYaUEX3jQ` remains `context_recovered_not_byte_verified`: the archived homepage content and pointer are preserved, but a separate byte-for-byte comparison with that AR transaction has not been recorded.
- `archive/hash-manifest.json` contains one semantic false positive: `7d6ac9...` is the JCS digest covered by Authority Manifest v1.0.2 and its EIP-712 signature, not an established SHA-256 of the Arweave transaction payload. The current mismatch label therefore does not prove that the repository copy differs from Arweave.

## Ethereum non-NFT records

| Role | Transaction | GitHub payload mirror |
|---|---|---|
| Guardianship Principles | `0xd082a3ced27ece935d4093fb001a9ebfba42b415f78de4377c8cda55338c6420` | Exact: `archive/guardian-principles/guardian-principles-original.md` |
| BTC↔ETH mapping attestation | `0x59cf33b1291de63c4840b79e7c674b8fc7c6a771d8a3ba2bb50def1fe55a71c6` | Exact raw calldata under `archive/legacy-pointers/eth-raw/` |
| Protocol mirror | `0x6652162e8e6c56ddc0d9476407b3b911e918d4e4683408440dc3af51c5bb63d5` | Exact reused payload: `bitcoin-inscription-mirrors/raw/97631551.txt` |
| Covenant mirror | `0x9c1bd6e21dc2370e8dbb6549b7ba13b4ea7ba7a192b3b876e0ec28b4633f1612` | Exact reused payload: `bitcoin-inscription-mirrors/raw/98369145.txt` |
| Accord mirror | `0x0affc8099ea965cd6d6a0d1cf9b93adb11f7e40ac41fffe1b0ca4637f39df665` | Exact reused payload: `bitcoin-inscription-mirrors/raw/98387475.txt` |
| BIP-322 notice | `0x55a0c131642f71c7b2386ccaac8bcee36563992226befb35363e978044a18e8f` | Exact raw calldata under `archive/legacy-pointers/eth-raw/` |
| Erroneous correction | `0x940300cba1acd7aa7078e614510400d4ec4b8961a2f05470d129c709b8cce3e6` | Exact raw calldata preserved as superseded evidence; it contains the 2,446-byte original Guardianship Principles text |
| Final correction | `0xa4023b1eb0de76993e1a8dcd571e5e033bf64e2d32a9a113b030b4094a19cf51` | Exact raw calldata under `archive/legacy-pointers/eth-raw/` |
| Guardianship Principles v1.1 | `0x7bdff0d696337ceb04539b44a746d0f13ce731ac25de259d8a4faf69b276a628` | Exact: `archive/guardian-principles/guardian-principles-v1.1.md` |
| BTC BIP-340 witness | `0x214d73b839ed95707410af3d5b8224a44a5dd310041d5e7ab1756ae9c5378137` | Witness metadata and the signed BTC object are mirrored |

These are Ethereum data transactions, attestations, notices, and witnesses. They are not NFTs and do not create new canonical authority.

## Large payload policy

Do not re-add large objects to the Git tree when a hash-verified Release mirror already exists, including:

- `j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk` — public Covenant archive;
- large flaw/fingerprint bundles already present as verified GitHub Release assets;
- later large evidence packages already covered by the release-aware verification system.

Their hashes and Release asset names are the mirror. Duplicating them in Git would increase repository fragility without improving provenance.

## Remaining qualifications

The legacy raw-payload mirroring task is complete for the identified missing AR and Ethereum non-NFT objects. Remaining work is verification hardening rather than missing-payload recovery:

1. optionally retrieve `Z_mRWz1jst-KUr4pyOyofFDLwj0H5bDHtPVYaUEX3jQ` and record a byte-for-byte comparison with `archive_legacy_index_2025_09.md`;
2. correct the Authority Manifest v1.0.2 hash semantics in the manifest generator instead of replacing a file using the wrong expected value;
3. continue treating sealed/non-public evidence as deliberately non-public rather than as a backup failure.
