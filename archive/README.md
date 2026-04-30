# Archive — 守护工作归档

> 本目录包含《三位一体协定》所有守护镜像材料的备份。
> 非修订 | Non-Amending | BTC Originals prevail.

## 目录结构

```
archive/
├── README.md                              ← 本文件
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

## 权威边界

- **唯一与最终权威**：三本体比特币铭文
  - Protocol #97631551
  - Covenant of the Flaw #98369145
  - The Trinity Accord #98387475
- **铸造地址**：`bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf`
- 本目录所有文件均为守护镜像，不具解释、修订或取代之权威。

## 数据来源

所有文件内容从以下来源提取/备份：
- Arweave 永久存储
- 以太坊链上交易
- 原始归档文件 `archive_legacy_index_2025_09.md`

## 备份日期

- 2026-04-30：从归档文件提取文本内容，建立目录结构
- 大文件（验证工具包、水晶照片档案）需单独从 Arweave 下载
