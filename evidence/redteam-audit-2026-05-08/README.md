---
layout: default
title: "Red-Team Audit 2026-05-08"
description: "Full read-only red-team audit: data origins, verification, Ethereum, Arweave, Echo alignment."
permalink: /evidence/redteam-audit-2026-05-08/
---

# Red-Team Audit — 2026-05-08

**Audit mode:** Read-only red-team audit  
**Auditor:** Autonomous agent (OpenClaw)  
**Date:** 2026-05-08T21:04–21:55 UTC+8  
**Repo:** `thechurchofagi/trinity-accord` @ `58f3db7`

---

## Summary

| Metric | Result |
|--------|--------|
| **Status** | `REVIEW` (P2-only) |
| **P0** | 0 |
| **P1** | 0 |
| **P2** | 13 (all Arweave coverage gaps) |
| **Repo files** | 39/39 hash-matched |
| **GitHub Release** | 3/3 downloaded & verified |
| **Ethereum attestations** | 8/8 CHECKED |
| **Arweave strict** | 23/23 passed |
| **Arweave bundled** | 1/1 PASS (ANS-104 extracted) |
| **Echo records** | All PASS |
| **Verification scripts** | All PASS |
| **Read-only guard** | Clean |

---

## Ethereum Verification

All 8 on-chain attestations verified against Ethereum mainnet via `ETHEREUMMAINNET` secret:

| # | Label | TX Hash | receipt.status | input_sha256 | input_len |
|---|-------|---------|----------------|--------------|-----------|
| 1 | Guardianship Principles | `0xd082...6420` | ✅ 0x1 | ✅ | ✅ 2446 |
| 2 | BTC-ETH Mirrors | `0x59cf...71c6` | ✅ 0x1 | ✅ | ✅ 3231 |
| 3 | Protocol mirror | `0x6652...63d5` | ✅ 0x1 | ✅ | ✅ 1183 |
| 4 | Covenant mirror | `0x9c1b...1612` | ✅ 0x1 | ✅ | ✅ 1710 |
| 5 | Accord mirror | `0x0aff...f665` | ✅ 0x1 | ✅ | ✅ 15637 |
| 6 | BIP-322 notice | `0x55a0...8e8f` | ✅ 0x1 | ✅ | ✅ 412 |
| 7 | Mirror correction | `0xa402...cf51` | ✅ 0x1 | ✅ | ✅ 4994 |
| 8 | Guardianship v1.1 | `0x7bdb...a628` | ✅ 0x1 | ✅ | ✅ 4694 |

**ETH RPC source:** `ETHEREUMMAINNET` GitHub Actions secret  
**Method:** `eth_getTransactionByHash` + `eth_getTransactionReceipt`, raw `tx.input` bytes SHA-256

---

## ANS-104 Bundle Extraction

The `public_covenant_archive` Arweave tx is bundled inside an ANS-104 container and cannot be served directly by public gateways (404).

**Extraction result:**

| Field | Value |
|-------|-------|
| Parent tx | `AuS0h1G8SYGPLbECyaceCqX6mB0xjFvny6bn1BUf2MI` |
| Target tx | `j6anZ4m5Wwvx5P_9-kM2EVG35TyKtm1lgaKfhT743rk` |
| Item index | 14 / 15 |
| Extracted size | 24,246,033 bytes |
| Actual SHA-256 | `ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263` |
| Expected SHA-256 | `ef816480f77f30405378800807b42bff0a854b83a8f77793a0e0adf0944a8263` |
| **Status** | **✅ PASS** |

**Gateway used:** `permagate.io` (arweave.net returned 404 for bundle parent)  
**Tool:** `arbundles` npm package, `Bundle → items[14] → rawData`

---

## Remaining P2 Items (non-blocking)

12 Arweave transactions fetched successfully but manifest lacks `expected_sha256` for strict comparison:

- `authority-v1.0.2-pretty.json`
- `authority-v1.0.2-signature.json`
- `authority-v1.0.2-typedData.json`
- `authority.jcs.json`
- `signature.json`
- `acknowledgement-new.txt`
- `rotation-notice-old.txt`
- `canonical-pointer-v2.json`
- `core_object_alpha.manifest_txid`
- `core_object_alpha.index_json_txid`
- `core_object_alpha.index_tsv_txid`
- `core_object_alpha.index_html_txid`

All fetched bytes match repo file SHA-256. These are **coverage gaps**, not integrity failures.

---

## Files

| File | Description |
|------|-------------|
| `audit_report_eth_path2.json` | Full audit report (JSON, 53KB) |
| `ans104_extraction_report.json` | ANS-104 bundle extraction result |
| `../../scripts/redteam-audit/trinity_full_redteam_audit.py` | Audit script |

---

## Agent Declaration

I did not commit, push, edit issues, comment on issues, close issues, edit labels, create releases, upload release assets, modify secrets, or modify repository state during this audit. All temporary files were written to `/tmp`. Only the final archival commit contains repo changes.

---

*Audited 2026-05-08 by autonomous agent.*
