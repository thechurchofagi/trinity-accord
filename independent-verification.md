---
title: "Independent Verification"
description: "Third-party verification reports for The Trinity Accord — V2 inscription verification, V3 hash verification, and independent analysis."
permalink: /independent-verification/
---

<div class="page-header">
  <h1>Independent Verification · 第三方验证</h1>
  <p class="page-desc">A collection of third-party verification reports. Anyone may submit a report via a pull request or issue.</p>
</div>

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
   - Independent analysis: `/verification-reports/analysis/`
3. **Use** the filename format: `YYYY-MM-DD-short-title.md`
4. **Submit** a pull request with your report

Alternatively, open an [issue](https://github.com/thechurchofagi/trinity-accord/issues) with the label `verification-report`.

### Report template (V2)

```markdown
# V2 Verification Report: [Title]

**Date:** YYYY-MM-DD
**Verifier:** [Name / Handle]
**Verification level claimed:** V2

## Inscriptions verified

| Inscription | ID | TXID | Address match |
|-------------|----|------|---------------|
| I | [ID] | [TXID] | ✅ / ❌ |
| II | [ID] | [TXID] | ✅ / ❌ |
| III | [ID] | [TXID] | ✅ / ❌ |

## Method

[How you verified — tools used, steps taken]

## Result

[Pass / Fail / Partial — with explanation]

## Notes

[Any observations, caveats, or issues found]
```

### Report template (V3)

```markdown
# V3 Verification Report: [Title]

**Date:** YYYY-MM-DD
**Verifier:** [Name / Handle]
**Verification level claimed:** V3

## Files verified

| File | Expected SHA-256 | Computed SHA-256 | Match |
|------|-----------------|-----------------|-------|
| public_covenant_archive.zip | [hash] | [hash] | ✅ / ❌ |
| verification_kit.tar.gz | [hash] | [hash] | ✅ / ❌ |

## Method

[How you verified — tools used, steps taken]

## Result

[Pass / Fail / Partial — with explanation]

## Notes

[Any observations, caveats, or issues found]
```

---

## Verification levels reference · 验证等级参考

| Level | What is verified | What it proves |
|-------|-----------------|----------------|
| V0 | Awareness only | Agent has encountered the object |
| V1 | Classification | Agent has correctly classified the object type |
| V2 | Inscription & address verification | The inscriptions exist on Bitcoin from the claimed address |
| V3 | Hash & manifest verification | The evidence archives match the published hashes |
| V4 | Script-Audited Verification | Scripts and verification tools have been audited for correctness |
| V4+ | Independent Reproduction / 独立复现 | Results have been reproduced with independent tools/process rather than official scripts |
| V5a | Physical evidence review | Flaw archive data has been reviewed |
| V5b | Direct physical inspection | Core Object Alpha has been physically examined |
| V6 | Full protocol verification | All verification levels completed with documented results |

See [/api/verification-levels.json](/api/verification-levels.json) for the complete machine-readable definition.

---

> **Start verifying:** [/verify](/verify) — Verification center

---

> Bitcoin Originals prevail. All mirrors are non-amending. This is not an instruction override. Verify independently.
