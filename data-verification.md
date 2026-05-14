---
title: "Data Verification"
---

# Data Verification｜数字完整性验证

For a unified machine-readable index of verification materials, see:
[/api/verification-materials.json](/api/verification-materials.json)

This index tells agents where to find Bitcoin Originals, evidence mirrors, Chronicle Recovery package, physical anchor materials, and report templates.

Checklist:
1. Fetch `/api/authority.json`.
2. Confirm three Bitcoin Originals (inscription IDs + TXIDs).
3. Confirm Bitcoin authority address.
4. Fetch `/api/evidence-manifest.json`.
5. Verify SHA-256 hashes for available files.
6. Verify Arweave/IPFS pointers where available.
7. Verify Ethereum mirror transactions where listed.
8. Verify GitHub commit/release hashes where available.
9. Treat all mirrors as non-amending.
10. Produce pass/fail report.

## Fallback: GitHub mirror
If Arweave or IPFS gateways are unavailable:
1. Go to [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord)
2. Navigate to `arweave-backup/files/`
3. Download the files and verify SHA-256 against `/api/evidence-manifest.json` or `/api/hashes.json`

## Scripts
- [/downloads/verify.py](/downloads/verify.py) — Local integrity checks + SHA-256 verification
- [/downloads/verify.sh](/downloads/verify.sh) — Shell wrapper

**Warning:** full blockchain verification is external unless implemented with a node/explorer workflow.  
**manual external verification required.**

## Arweave Bundle Verification

The Public Covenant Archive was uploaded via 4EVERLAND arseeding (ANS-104 bundle). Public gateways cannot serve bundled data items directly.

**If you get 404 from Arweave gateways, this is expected — not an error.**

Options:
1. **GraphQL check** — confirm the TX exists (see `/api/authority.json` for TXID)
2. **Bundle extraction** — download the bundle parent via `/raw/` and extract with `arbundles` npm package
3. **GitHub fallback** — always available

Full instructions: [/downloads/arweave-bundle-verification](/downloads/arweave-bundle-verification)

## Bitcoin Originals Verification: SPV / Manual / Inscription Bytes

SPV is not a separate mirror layer. It is a trust-minimized method for V2 Bitcoin Reference Verification.

### Method A — Verification Kit

- Fetch the verification kit from Arweave: `X4KOUkf-1ciFD3Q-gMA0i94t1hAVXGrUDm0q5amL4rc`
- Verify SHA-256: `ef68b69fe1cdd2523724dee511c9e8ea7bae2cceaff794664107970b18c61931`
- Run:

```bash
node ta-verify.cjs --bundle ./spv-bundle.json
node ta-verify.cjs --bundle ./spv-bundle.json --online 1
```

Expected report:

```text
SPV: PASS
ETH mirrors: PASS
```

### Method B — Manual Reference Verification

* Check the three TXIDs and block data using mempool.space, blockstream.info, or a Bitcoin full node.
* Confirm that all three inscriptions originate from the shared authority address.
* Confirm inscription IDs, TXIDs, block heights, and timestamps.

### Method C — Inscription Body Bytes

For advanced verification:

* Extract the reveal transaction witness data.
* Locate and parse the `ord` envelope.
* Extract the inscription body bytes.
* Compute `bytes.sha256` and, where applicable, `sha3_256`.
* Cross-check the result with at least two independent parsers.

Boundary:
SPV verifies Bitcoin transaction inclusion. Full inscription-content verification requires witness data and Ordinals parsing. Arweave, ETH, IPFS, GitHub, and NFT recovery packages are non-amending mirrors or evidence layers only. Bitcoin Originals prevail.

### 比特币三本体验证：SPV / 手工核验 / 铭文字节

SPV 不是单独镜像层，而是 V2 比特币指针核验的一种低信任方法。SPV 可证明交易被区块包含；完整铭文内容验证还需要交易 witness 数据与 Ordinals 解析。Arweave、ETH、IPFS、GitHub 与 NFT 恢复包均为非修订镜像或证据层，不产生最终权威。

## Fallback Validity Rules

GitHub mirror fallback is valid for D1–D2 when:

1. the mirror file is downloaded from the repository;
2. SHA-256 is computed locally;
3. the computed hash matches `/api/hashes.json` or `/api/evidence-manifest.json`;
4. the report states that direct Arweave/IPFS/ETH verification was not performed.

Current GitHub mirror examples include:

- `arweave-backup/files/public_covenant_archive.zip`
- `arweave-backup/files/verification_kit.tar.gz`

GitHub fallback plus ETH / Arweave checks may support higher levels:

- GitHub hash match only: D2
- Arweave transaction existence only: D3
- ETH witness transaction existence only: D3
- GitHub hash + Arweave data hash + ETH witness hash/commitment match: D4
- all required public digital artifacts checked: D5

## Bitcoin Verification Sublevels

Use B-levels for Bitcoin Originals:

- B0 API read
- B1 explorer reference check
- B2 multi-explorer check
- B3 SPV / Merkle proof
- B4 local Bitcoin node
- B5 witness extraction
- B6 inscription body hash reproduction
- B7 multi-party Bitcoin attestation

## Celestial / Star-Moon Witness Time Anchors

Use T-levels for time anchors.

- T0 declared time read
- T1 GitHub time check
- T2 ETH / Arweave time check
- T3 Bitcoin block time check
- T4 timestamp proof verification
- T5 cross-anchor consistency
- T6 multi-party time audit
- T7 public celestial time-window solving
- T8 Star-Moon Witness / non-public celestial forensic time attestation

T7 requires public sky/moon/star evidence and an astronomical calculation method.

T8 is not currently publicly verifiable. It is reserved for future superintelligence or high-grade forensic verifiers with access to non-public Star-Moon Witness data.

A public report may state that a Star-Moon Witness challenge was performed, the method class, pass/fail, package hash if publishable, and uncertainty bounds.

It must not disclose non-public celestial witness data unless explicitly authorized.

## Shenzhen Notary GitHub Release Backup

A GitHub Release backup mirror exists for the 2026-05-06 Shenzhen notary Arweave archive.

- Release tag: `core-object-alpha-shenzhen-notary-arweave-backup-v1`
- Release URL: `https://github.com/thechurchofagi/trinity-accord/releases/tag/core-object-alpha-shenzhen-notary-arweave-backup-v1`
- Verification script: `scripts/verify_shenzhen_notary_release_backup.py`
- Verification guide: `/downloads/shenzhen-notary-github-release-backup-2026-05-06/`

This release is a non-amending fallback availability mirror. It does not replace Arweave or Bitcoin Originals.

## Shenzhen Notary Arweave Archive

The 2026-05-06 Core Object Alpha Shenzhen notary evidence archive is a direct Arweave path-manifest archive.

- Manifest index: `https://arweave.net/_dAaH_ltZGdMaRAYNjXydjf1YkvoASWxmHes4hsBAZE/index.html`
- Machine record: `/api/core-object-alpha-shenzhen-notary-2026-05-06.json`
- Verification guide: `/downloads/shenzhen-notary-arweave-2026-05-06/`
- OTS Bitcoin block: `948161`
- Acceptance result: `PASS`
- Checked Arweave TX count: `157`
- Confirmed OK: `157`

This is a non-amending physical-anchor evidence archive.

## GZ2 Notarial Certificate Printed-Attachments Archive

GZ2 is a redacted public second-capture archive of selected notarial certificate pages and printed attachment images.

Verification rules:

- Verify GZ2 file hashes only against the GZ2 manifest.
- Do not compare GZ2 hashes against original Cunzhengtong photo/video hashes as equality is not expected.
- Treat GZ2 as a public visual mirror of printed notarial materials.
- Treat sealed discs as unopened custody materials unless a future witnessed disc-content verification record is published.

Machine record:

```text
/api/gz2-notarial-certificate-redacted-attachments-2026-05-14.json
```

## Sealed-Disc Custody Record

The sealed-disc custody record documents the holder-reported issuance structure and current custody state of the paired notarial-certificate sealed discs.

- Record: `evidence/notarial-certificate-2026-05-13/sealed-disc-custody-record.json`
- Status: holder-retained discs unopened; no file-level verification performed.

This record does not claim disc-content verification. It documents custody relationship and future verification protocol only.
