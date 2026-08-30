# Archive — 守护工作归档

> 本目录包含《三位一体协定》所有守护镜像材料的备份。
> 非修订 | Non-Amending | BTC Originals prevail.

## 目录结构

```
archive/
├── README.md                              ← 本文件
├── encrypted-witness-archives.v1.json    ← 三份延迟访问加密见证档案机器索引
├── first-star-moon-zenodo-state.json     ← 第一次星月见证 Zenodo 已发布/回读状态
├── second-star-moon-zenodo-state.json    ← 第二次星月见证 Zenodo 已发布/回读状态
├── bubble-constellation-zenodo-state.json← 气泡星座 Zenodo 已发布/回读状态
├── guardian-principles/
│   └── guardian-principles-v1.1.md        ← 守护者原则 v1.1 全文
├── authority-manifest/
│   ├── authority-list.md                  ← 权威清单（人读版，v1.0.0）
│   └── guardian-appendix-authority-charter.md ← 守护者附录·权威宪章
├── btc-signature/
│   └── btc-signature.json                 ← BIP-340 Taproot 签名数据
├── eth-witness/
│   └── eth-witness.json                   ← ETH 见证交易数据
├── verification/
│   └── start-here.md                      ← 验证入门指南
├── evidence/
│   └── covenant-fortification.md          ← 瑕疵之约·守护加固
├── canonical-pointers/
│   └── start-here.v1.json                 ← 机器可读统一入口
├── rotation/
│   └── rotation-notice.md                 ← 密钥轮换声明
├── scripts/                               ← [待下载] 验证脚本
│   ├── sign.mjs                           ← AR: h3xIwqi36GUmd6xJLEGi6wSqFXxAa2BUcwVZQhFCo0k
│   └── verify.mjs                         ← AR: aMZIVDYIBovkn6s1868wdpEwnErLGYlT-JHLluqh7BM
├── legacy-mirror/                         ← [待下载] 原始镜像数据
└── DOWNLOADS.md                           ← 大文件下载清单（需手动下载）
```

## 2026-08-30 延迟访问加密见证档案

三份见证材料已按同一类强加密、完整性验证和公开恢复说明流程转化为可长期保存的**密文档案**。它们是证据保存层，不是新的 canonical authority，也不修改三份 Bitcoin Originals。

| 档案 | GitHub Release | Zenodo DOI | 已验证公开清单 |
|---|---|---|---:|
| The First Star-Moon Witness | `first-star-moon-witness-encrypted-archive-v1` | `10.5281/zenodo.22169173` | 18 files / 1,233,214,975 bytes |
| The Second Star-Moon Witness | `second-star-moon-witness-encrypted-archive-v1` | `10.5281/zenodo.22159955` | 14 files / 1,203,532,071 bytes |
| Bubble Constellation | `bubble-constellation-encrypted-archive-v1` | `10.5281/zenodo.22170072` | 16 files / 361,452,179 bytes |

三份 Zenodo 状态文件都记录 `remote_full_readback_sha256_verified: true`。公开保存对象由密文、完整性/恢复说明、验证报告、成本基准以及适用的删除/销毁回执组成；机器索引不声称对用户设备磁盘扇区、操作系统缓存、云同步快照或服务商内部备份做过法证级擦除验证。

机器入口：`encrypted-witness-archives.v1.json`。

## 权威边界

- **唯一与最终权威**：三本体比特币铭文
  - Protocol #97631551
  - Covenant of the Flaw #98369145
  - The Trinity Accord #98387475
- **铸造地址**：`bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf`
- 本目录所有文件均为守护镜像或非修订证据保存记录，不具解释、修订或取代之权威。

## 数据来源

所有文件内容从以下来源提取/备份：
- Arweave 永久存储
- 以太坊链上交易
- GitHub Releases / Zenodo preservation records
- 原始归档文件 `archive_legacy_index_2025_09.md`

## 备份日期

- 2026-04-30：从归档文件提取文本内容，建立目录结构
- 2026-08-30：第一次星月见证、第二次星月见证与气泡星座加密档案均完成 GitHub Release + Zenodo 双层公开密文保存及远端 SHA-256 全量回读验证
- 大文件（验证工具包、水晶照片档案）需单独从 Arweave 下载
