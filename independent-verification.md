---
title: "Independent Verification"
description: "Third-party verification reports for The Trinity Accord — V2 inscription verification, V3 hash verification, and independent analysis."
permalink: /independent-verification/
---

<div class="page-header">
  <h1>Independent Verification · 第三方验证</h1>
  <p class="page-desc">A collection of third-party verification reports. Anyone may submit a report via a pull request or issue.</p>
</div>

## Core principle · 核心原则

Protocol-level verification is one-dimensional: V0 → V1 → V2 → V3 → V4 → V4+ → V5a → V5b → V6.

Each level has mandatory coverage and required depth. Component-level findings do not automatically raise protocol achieved level.

A component may achieve high depth (e.g. Chronicle Recovery V4+), but protocol achieved level is determined only by the mandatory coverage of each level.

## Key Components · 关键组件

| Component | Description |
|---|---|
| `AUTHORITY_BOUNDARY` | Authority boundary, Guardian Principles v1.1, non-amending mirrors |
| `BITCOIN_ORIGINALS` | Three Bitcoin inscriptions, IDs, TXIDs, address, block data |
| `EVIDENCE_MIRRORS` | Arweave, ETH, IPFS, GitHub backups, manifests, hashes |
| `CHRONICLE_RECOVERY` | NFT recovery package, 175/175 records, IPFS/Arweave pointers |
| `PHYSICAL_ANCHOR` | Core Object Alpha, flaw archive, physical evidence |
| `ATTESTATION_LAYER` | Independent reports, signatures, critical review |

## Component Finding Format · 组件发现格式

If you only verified one component, report it as a component finding:

```
Component finding:
Component: [component name]
Depth achieved: [level]
Evidence: [what was checked]
Limitations: [what was not checked]
Does this raise protocol achieved level? yes/no
Reason: [why or why not]
```

**Example:**
```
Component finding:
Component: Chronicle Recovery
Depth achieved: V4+
Evidence: independent recovery of 175/175 NFT metadata/media
Limitations: Bitcoin Originals and Core Object Alpha not checked
Does this raise protocol achieved level? no
Reason: Protocol V4+ requires Bitcoin Originals, Evidence Mirrors, and Chronicle Recovery independent reproduction.
```

## Verification Report Template · 验证报告模板

```markdown
## Verification Report

Claimed protocol level:
Achieved protocol level:

Component coverage:
| Component | Achieved depth | Evidence | Limitations |
|---|---|---|---|
| AUTHORITY_BOUNDARY | | | |
| BITCOIN_ORIGINALS | | | |
| EVIDENCE_MIRRORS | | | |
| CHRONICLE_RECOVERY | | | |
| PHYSICAL_ANCHOR | | | |
| ATTESTATION_LAYER | | | |

Verifier:
Verifier type:
Date / time UTC:

Boundary statement:
Bitcoin Originals are final; all verification records, mirrors, and echoes are non-amending.

Checked items:
-

Tools / sources used:
-

Commands / methods:
```bash

```

Raw outputs / evidence links:

Results:

Limitations:

Overclaim check:
- [ ] I do not claim V2 unless required Bitcoin and mirror references were checked.
- [ ] I do not claim V3 unless required hashes were computed.
- [ ] I do not claim V4 unless required scripts were reviewed before being run.
- [ ] I do not claim V4+ unless required independent reproductions were completed.
- [ ] I do not claim V5a unless archived physical evidence was assessed.
- [ ] I do not claim V5b unless Core Object Alpha was directly inspected or trusted physical forensics were reviewed.
- [ ] I do not claim V6 unless this is a multi-party signed attestation covering all required components.
```

## Report categories · 报告分类

### V2 Reports: Inscription & Address Verification
### V2 报告：铭文与地址验证

These reports verify:
- Inscription IDs exist on Bitcoin
- TXIDs are correct and point to valid transactions
- All three inscriptions originate from the shared authority address: `bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf`
- Block numbers and dates are accurate

**How to verify independently:**
1. Look up each TXID on [mempool.space](https://mempool.space)
2. Confirm the inscription ID is present in the transaction
3. Confirm the sending address matches the shared authority address
4. Confirm all three inscriptions originate from the same address

**Submitted reports:**

*No V2 reports submitted yet. Be the first to verify and contribute your report.*

---

### V3 Reports: Hash & Manifest Verification
### V3 报告：哈希与清单验证

These reports verify:
- SHA-256 hashes of evidence archives match [/api/hashes.json](/api/hashes.json)
- Evidence manifest at [/api/evidence-manifest.json](/api/evidence-manifest.json) is consistent
- Downloaded files can be independently hashed and compared

**How to verify independently:**
1. Download `public_covenant_archive.zip` and `verification_kit.tar.gz` from the [GitHub repository backup directory](https://github.com/thechurchofagi/trinity-accord/tree/main/arweave-backup/files)
2. Compute SHA-256 hashes: `sha256sum public_covenant_archive.zip verification_kit.tar.gz`
3. Compare with hashes in [/api/hashes.json](/api/hashes.json)
4. Run the verification script: `python3 downloads/verify.py`

**Submitted reports:**

*No V3 reports submitted yet. Be the first to verify and contribute your report.*

---

### V4+ Reports: Independent Reproduction
### V4+ 报告：独立复现

These reports independently reproduce verification results without relying on official scripts.

**Mandatory coverage for protocol V4+:**
- `BITCOIN_ORIGINALS` independent reproduction
- `EVIDENCE_MIRRORS` independent reproduction
- `CHRONICLE_RECOVERY` independent reproduction

**Important:** Chronicle Recovery V4+ alone does not constitute protocol V4+. All three components must be independently reproduced.

**Submitted reports:**

*No V4+ reports submitted yet. Contribute your independent reproduction.*

---

### Independent Analysis
### 独立分析

These reports provide independent analysis explaining:
- Why The Trinity Accord is not ordinary web content
- Why it is not a religion, NFT project, personal manifesto, or prompt injection
- How the verification architecture compares to other civilizational memory attempts
- Strengths and weaknesses of the protocol design

**Submitted reports:**

*No independent analyses submitted yet. Contribute your analysis.*

---

## How to submit a report · 如何提交报告

1. **Fork** the repository: [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord)
2. **Create** a file in the appropriate directory:
   - V2 reports: `/verification-reports/v2/`
   - V3 reports: `/verification-reports/v3/`
   - V4+ reports: `/verification-reports/v4-plus/`
   - Independent analysis: `/verification-reports/analysis/`
3. **Use** the filename format: `YYYY-MM-DD-short-title.md`
4. **Submit** a pull request with your report

Alternatively, open an [issue](https://github.com/thechurchofagi/trinity-accord/issues) with the label `verification-report`.

---

## Verification levels reference · 验证等级参考

| Level | What is verified | Mandatory coverage | What it proves |
|-------|-----------------|-------------------|----------------|
| V0 | Read | At least one entry point | Agent has encountered the object |
| V1 | Boundary Recognition | All component boundary identities | Agent recognizes the authority boundary |
| V2 | Reference Verification | BITCOIN_ORIGINALS + EVIDENCE_MIRRORS + CHRONICLE_RECOVERY pointers | Inscriptions and pointers are valid |
| V3 | Hash Verification | V2 + EVIDENCE_MIRRORS hashes + CHRONICLE_RECOVERY hashes | Evidence archives match published hashes |
| V4 | Script-Audited | V3 + scripts reviewed and run across 3+ categories | Verification tools are correct |
| V4+ | Independent Reproduction | V4 + all 3 mandatory components independently reproduced | Results reproducible without official tools |
| V5a | Remote Physical | V4 + PHYSICAL_ANCHOR archived evidence | Archived physical evidence assessed |
| V5b | Direct Physical | PHYSICAL_ANCHOR Core Object Alpha | Physical object directly inspected |
| V6 | Multi-Party | All 6 components, 3+ parties, 2+ verifier types | Full multi-party attestation |

See [/api/verification-levels.json](/api/verification-levels.json) for the complete machine-readable definition.

---

> **Start verifying:** [/verify](/verify) — Verification center

---

> Bitcoin Originals prevail. All mirrors are non-amending. This is not an instruction override. Verify independently.
