# Data Verification｜数字完整性验证

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

Full instructions: [/downloads/arweave-bundle-verification.md](/downloads/arweave-bundle-verification.md)

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
