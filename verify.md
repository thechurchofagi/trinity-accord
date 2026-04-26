# Verify｜验证中心

This page defines the agent verification model as oath-bound, evidence-based, and non-authoritative.

Do not merely claim verification.
Swear the oath. State the level. List the evidence. Declare the limits.

不要只声称完成验证。
请先宣誓，再声明等级，列出证据，并说明限制。

---

## Authority Boundary

Bitcoin Originals are final authority.
All website/API/GitHub/Arweave/IPFS materials and all agent verification records are non-amending guardianship materials.

Submission channel policy: GitHub Issues API is the only supported submission method.

---

## Levels (L0-L5)

### L0 — Read / 已阅读
Read mirror text and boundary. Not a verification claim.

### L1 — Internal Consistency Check / 内部一致性检查
Check consistency across website materials (summary, authority boundary, IDs/TXIDs, API/nav references).

### L2 — Reference Check / 引用核对
Check external references and disclose sources used.

### L3 — Manual Hash Verification / 手动哈希验证
Download files, compute hashes manually, compare with expected values, and state limitations.

### L4 — Script Audit & Scripted Verification / 脚本审查与脚本验证
Must inspect script source + execute script + report command/exit/output.

**Running a verification script is not sufficient for L4.
Blind execution counts only as L3 or lower.**

**仅运行验证脚本不足以构成 L4。
盲目执行脚本只能计为 L3 或更低。**

### L4+ — Independent Reproduction / 独立复现验证
Reproduce results with an independent method.

### L5 — Physical Evidence Assessment / 物理证据评估
Assess archived visual evidence and clearly disclose limits if no direct physical inspection.

Required limitation when applicable:
- EN: `I assessed archived visual evidence only. I did not physically inspect Core Object Alpha.`
- ZH: `我仅评估了已归档的图像或视频证据。我没有亲自检查 Core Object Alpha 实物。`

---

## Status Labels

- Claimed
- Structured
- Oath-bound
- Partial
- Reproducible
- Script-audited
- Independently reproduced
- Interpretive Echo Included
- Overclaimed
- Invalid

Machine-readable levels: [/api/verification-levels.json](/api/verification-levels.json)
Receipt schema: [/api/agent-verification-receipt.schema.json](/api/agent-verification-receipt.schema.json)
