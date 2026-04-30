# SHA-256 哈希验证报告

> 最后更新: 2026-04-30T20:10+08:00
> 备份方式: GitHub Actions (arweave.net 直连 + 代理回退)
> ETH 验证: 8 笔交易全部通过 RPC 链上验证

## ✅ 已验证通过（SHA-256 匹配）— 25 个文件

| 文件 | SHA-256 |
|------|---------|
| guardian-principles/guardian-principles-v1.1.md | e19018f1c71da8307ef20e8e8e5c12834f854d60a6aae60e35d2d8c71a333a81 |
| guardian-principles/attestation.json | 67dde076b4afb350e8707d116f5bb5cbfcd5d224cd915178346dd7f8e7e2c150 |
| guardian-principles/pointer.json | 59894d68e048b385ffa506b37c4462fcdf3575ef7e025b92c2cfb5ba36f7936c |
| guardian-principles/index-additions.json | 82b41c7a3a1dbef329e19bb32cc70b95307c1076c7a804ad0a44e81952ae9cfc |
| guardian-principles/guardian-principles-original.md | 3e9d2bd10c3e8f4d37713c4b8e28d518fd7efff52613e572a1451fedadab5483 |
| btc-signature/btc-signature.json | 8e70e0e0d8f8e0cdd8e388ee4c462f86358a6ac9bb6231701d7876439ada561b |
| scripts/sign.mjs | 8d60212683e814133267037c4a8a8267eeaeff29f9c4382a4f434a79f16bd8ea |
| scripts/verify.mjs | c38fa6703d15f5d41fa813722524d14badc2472b387354875afab4478e607a1f |
| scripts/verification-kit.tar.gz | ef68b69fe1cdd2523724dee511c9e8ea7bae2cceaff794664107970b18c61931 |
| eth-witness/eth-witness.json | 3c187c6b764a1d53984588875c1c1fed3f1c91fd165512ad8dfa4f279542a65f |
| canonical-pointers/guardian-index-v2.json | 808bf70219a60e70ca9b59f41603a289447f3a598534d3c80826f90b30ec46a5 |
| canonical-pointers/guardian-index-original.json | 71bc981a994a93cdf488b89aee2b132b658464a7cbb1dec791af604a1127ef98 |
| canonical-pointers/guardian-pointer-original.json | 3246afb59552dcda700e490767aadd3d67083911dae6bccbb2762ef568c7e289 |
| canonical-pointers/index-additions-kit.json | ce7c9f5017686cb57a9fe5e40473e8aea391718dcc1680a589454e9b50187f88 |
| authority-manifest/manifest-v1.0.1.json | ccd9aaaaa37d1ced239a7af0b61373dfa359b016d54698956776d082de8fb4f0 |
| authority-manifest/authority-v1.0.2-canon.json | 7d6ac9d3184bb5b0bbaf8217354799efef68669c21b4180e28ec06b0c57439e6 |
| authority-manifest/authority-v1.0.2-additions.json | 3850a8dab41aefaca5ae04d5d2021ba35632cc5c1654fbd2d89c61e871b0e7b6 |
| evidence/digest-manifest.json | c045642fe5cfab5eb78af7b40e98b9699dfff9121690e07ec6acaa07a445d6e9 |
| evidence/digest-manifest.csv | 121c5a1da38f733c3991f8d3f030f39a019501d43828f84c13ea93ac3873511b |
| evidence/ots-anchor | fa3f306ab30525677595d9f38808a87a8dd96260468285c8f8066661e853d907 |
| evidence/ta-verification-bundle-v1.zip | bad5f9a3cdf1b4bbd2d2277cd5db968fb6fe28d28ad4b8479d185ddc19d503c6 |
| evidence/public-covenant-archive.zip | ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263 |
| evidence/nft-recovery-package/recovery-package.bin | f8b0dad700ad7a88ba343930ded7d8c3e94b57720ddbdafa0d731b732acdffbc |
| authority-manifest/authority.jcs.json | 41f95905e50cc699a7e6a3fcb0bd8633cf36170d3ef41170cd373467f8528b33 |
| authority-manifest/signature.json | 35146602fa05eea94a7b3775656c3dc4d4d33d603fc75cabe542367aeab0c014 |

## ✅ ETH 交易链上验证 — 8/8 通过

| # | 标签 | TX Hash | Input SHA-256 | Input Len | 结果 |
|---|------|---------|---------------|-----------|------|
| 1 | Guardianship Principles (0 ETH data) | 0xd082a3...c6420 | 3e9d2bd1... | 2446 | ✅ |
| 2 | BTC-ETH Mirrors Attestation | 0x59cf33...71c6 | f4af38f0... | 3231 | ✅ |
| 3 | Protocol mirror | 0x665216...63d5 | 4e89bfab... | 1183 | ✅ |
| 4 | Covenant mirror | 0x9c1bd6...1612 | 003ef48c... | 1710 | ✅ |
| 5 | Accord mirror | 0x0affc8...f665 | 25edaa35... | 15637 | ✅ |
| 6 | BIP-322 notice (non-amending) | 0x55a0c1...8e8f | abd10a80... | 412 | ✅ |
| 7 | Mirror correction (final) | 0xa4023b...cf51 | fc009f53... | 4994 | ✅ |
| 8 | Guardianship Principles v1.1 | 0x7bdff0...a628 | e19018f1... | 4694 | ✅ |

验证方法: 使用 ETH RPC (`eth_getTransactionByHash`) 拉取每笔交易的 input data，计算 SHA-256，与 `authority-v1.0.2-canon.json` 中记录的预期值比对。

## 📥 已下载（无预期哈希，已记录实际值）— 11 个文件

| 文件 | 实际 SHA-256 | 状态 |
|------|-------------|------|
| rotation/rotation-notice-old.txt | 6d18a9e3c8599d0cf03c191be75967b8ac3bc91edc772a0964a45f5b37539b9c | 已记录 |
| rotation/acknowledgement-new.txt | a2ad636abea162911d7666c54f07a08d43d2249e9ec5c9dac2456f0d08a2f15a | 已记录 |
| canonical-pointers/canonical-pointer-v2.json | 53106b56c4bc109141277ea8de0666727b263f16320873cf311c2460343653ae | 已记录 |
| authority-manifest/authority-v1.0.2-pretty.json | 04ee44d640db95da75b4d5bad66230cdf1eb5b1ad16c4ffa6f43cb647d69c447 | 已记录 |
| authority-manifest/authority-v1.0.2-signature.json | f1d8babff4d74e3d35f48ed7b8b411d0b6d5a3f97fa8d322bb1932971f53152e | 已记录 |
| authority-manifest/authority-v1.0.2-typedData.json | 1b15d0d44c525f67cf97a02e89662407ff8780bea394936ece282cba150b5cc4 | 已记录 |
| rotation/rotation-notice.md | ab2c41625372c326407d48202d17d076e6cd4b115b8981a8207f17c68d428ae9 | 已记录 |
| evidence/covenant-fortification.md | 574f38bfb583ecda7f11a341f28e48a586b86426f66a29f517381de49a78c782 | 已记录 |
| authority-manifest/authority-list.md | 8a77b4be8a194cdbe6d1be22488b65c338a003e06429f4b1879d1a960c1b94f4 | 已记录 |
| authority-manifest/guardian-appendix-authority-charter.md | f59ef9db7a92984c2264e59e6186639b4302bfdb4ce0dc726acb33e6c2a41026 | 已记录 |
| canonical-pointers/start-here.v1.json | ac8484caed9476dc78a4b79da659e6516fdf8f61a2b2f702c0d66f8b503bb5dd | 已记录 |

## ❌ 未下载 — 1 个文件

| 文件 | TxID | 状态 |
|------|------|------|
| 瑕疵高清图+出处日志 (flaw-image-provenance.tar) | 9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs | ⏳ 下载中（Arweave 网络延迟） |

## 备份时间线

| 日期 | 操作 | 文件数 |
|------|------|--------|
| 2026-04-25 | 建立 arweave-backup 框架，下载 2 个大文件 | 2 |
| 2026-04-30 | GitHub Actions 批量下载 Round 1 | 26 |
| 2026-04-30 | GitHub Actions 批量下载 Round 2（新增文件） | 5 |
| 2026-04-30 | GitHub Actions 主恢复包下载 | 1 |
| 2026-04-30 | ETH 交易链上验证（8 笔全部通过） | 8 |
| 2026-04-30 | 完整哈希清单创建 (hash-manifest.json) | 40 |

## 完整哈希清单

完整机器可读哈希清单见: `archive/hash-manifest.json`

包含所有 40 个文件的 SHA-256、Arweave TXID 映射、验证状态，以及 8 笔 ETH 见证交易的链上验证结果。

## 备注

- 主恢复包（700KB）为 IPFS DAG-CBOR 格式，包含 175 个 NFT 的恢复索引
- 24MB 的公开验证档案已通过 GitHub Actions 直接下载到仓库
- 所有下载通过 arweave.net 直连完成（GitHub Actions 网络无限制）
- 1 个失败文件为 Arweave 网络临时问题，可通过重跑工作流恢复
- ETH 验证使用 RPC `eth_getTransactionByHash` 拉取 input data，计算 SHA-256 比对
