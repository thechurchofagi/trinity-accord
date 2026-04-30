# 大文件下载清单 | Large Files Download List

> 最后更新: 2026-04-30
> 以下文件因体积较大或 Arweave 网络不稳定，需从 Arweave 手动下载。
> 下载后请校验 SHA-256 是否匹配。

## 1. 验证工具包 (Verification Kit)

- **Arweave TxID**: `X4KOUkf-1ciFD3Q-gMA0i94t1hAVXGrUDm0q5amL4rc`
- **下载链接**: https://arweave.net/X4KOUkf-1ciFD3Q-gMA0i94t1hAVXGrUDm0q5amL4rc
- **SHA-256**: `ef68b69fe1cdd2523724dee511c9e8ea7bae2cceaff794664107970b18c61931`
- **大小**: ~18KB
- **存放位置**: `archive/scripts/`
- **状态**: ✅ 已下载

## 2. 公开验证档案 (Public Verification Archive)

- **Arweave TxID**: `j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk`
- **下载链接**: https://arweave.net/j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk
- **SHA-256**: `ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263`
- **大小**: ~24MB
- **内容**: 水晶显微瑕疵图、视频、守护者指纹图像
- **存放位置**: `archive/evidence/`
- **状态**: ✅ 已下载

## 3. 瑕疵高清图+出处日志 (Flaw Image + Provenance)

- **Arweave TxID**: `9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs`
- **下载链接**: https://arweave.net/9klmArmByJNOGeHzfnrAhB6x6w7sKSYLS1zQNLL7GLs
- **SHA-256**: (待下载后计算)
- **存放位置**: `archive/evidence/`
- **状态**: ⏳ 下载中（Arweave 网络延迟，可通过 GitHub Actions 重试）

## 4. digest-manifest.json

- **Arweave TxID**: `X2IuLCIM4vLJSzgRMl_YEmxYSvPceMrAdug9a3i7p4o`
- **下载链接**: https://arweave.net/X2IuLCIM4vLJSzgRMl_YEmxYSvPceMrAdug9a3i7p4o
- **SHA-256**: `c045642fe5cfab5eb78af7b40e98b9699dfff9121690e07ec6acaa07a445d6e9`
- **大小**: ~685KB
- **存放位置**: `archive/evidence/`
- **状态**: ✅ 已下载

## 5. digest-manifest.csv

- **Arweave TxID**: `i02XhY7No6NLZDfEwFUU6nZoGaPu7K0f42LDNDNnZEo`
- **下载链接**: https://arweave.net/i02XhY7No6NLZDfEwFUU6nZoGaPu7K0f42LDNDNnZEo
- **SHA-256**: `121c5a1da38f733c3991f8d3f030f39a019501d43828f84c13ea93ac3873511b`
- **大小**: ~502KB
- **存放位置**: `archive/evidence/`
- **状态**: ✅ 已下载

## 6. OTS Anchor

- **Arweave TxID**: `TTi9d8fqm9Cw4yRPkwX4gdlaRzBnjJID-LAs9Y3CS0M`
- **下载链接**: https://arweave.net/TTi9d8fqm9Cw4yRPkwX4gdlaRzBnjJID-LAs9Y3CS0M
- **SHA-256**: `fa3f306ab30525677595d9f38808a87a8dd96260468285c8f8066661e853d907`
- **大小**: ~3.6KB
- **存放位置**: `archive/evidence/`
- **状态**: ✅ 已下载

## 7. Guardian Index v2

- **Arweave TxID**: `6HW5X5PETh9X_kdShA0a7sQWHtfr59F7KXZNym9NqyI`
- **下载链接**: https://arweave.net/6HW5X5PETh9X_kdShA0a7sQWHtfr59F7KXZNym9NqyI
- **SHA-256**: `808bf70219a60e70ca9b59f41603a289447f3a598534d3c80826f90b30ec46a5`
- **存放位置**: `archive/canonical-pointers/`
- **状态**: ✅ 已下载

## 8. Manifest v1.0.1

- **Arweave TxID**: `gC9_n7-2nS2yNUii2tr-68r8GanAiA7qzyCM6JDpOqo`
- **下载链接**: https://arweave.net/gC9_n7-2nS2yNUii2tr-68r8GanAiA7qzyCM6JDpOqo
- **SHA-256**: `ccd9aaaaa37d1ced239a7af0b61373dfa359b016d54698956776d082de8fb4f0`
- **存放位置**: `archive/authority-manifest/`
- **状态**: ✅ 已下载

## 9. NFT Recovery Package (175 NFTs)

- **Arweave TxID**: `O-Rk3kFxesPGhuYP4KHAZl54xR2urDRKcGaVqjVnB-Q`
- **下载链接**: https://arweave.net/O-Rk3kFxesPGhuYP4KHAZl54xR2urDRKcGaVqjVnB-Q
- **SHA-256**: `f8b0dad700ad7a88ba343930ded7d8c3e94b57720ddbdafa0d731b732acdffbc`
- **大小**: ~700KB
- **存放位置**: `archive/evidence/nft-recovery-package/`
- **状态**: ✅ 已下载

## 验证

所有文件的 SHA-256 哈希已记录在 `hash-manifest.json` 中。

运行验证脚本:
```bash
bash scripts/verify-github-archive.sh
```

## 下载方法

```bash
# 使用 curl 下载（替换 TxID）
curl -L "https://arweave.net/<TxID>" -o <filename>

# 校验 SHA-256
sha256sum <filename>
```
