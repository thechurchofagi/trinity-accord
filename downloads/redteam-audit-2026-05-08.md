---
layout: default
title: "Red-Team Audit 2026-05-08"
description: "Read-only red-team audit: data origins, Ethereum attestations, Arweave bundle extraction, Echo alignment."
permalink: /downloads/redteam-audit-2026-05-08/
---

# Red-Team Audit — 2026-05-08

Full read-only red-team audit covering data origins, GitHub mirrors, Ethereum attestations, Arweave verification (including ANS-104 bundle extraction), Echo record alignment, and verification script integrity.

## Results

- **P0:** 0
- **P1:** 0
- **Ethereum:** 8/8 CHECKED (all receipt.status=0x1, all input hashes matched)
- **Arweave:** 23/23 strict pass + 1/1 bundled origin verified
- **Repo:** 39/39 files hash-matched
- **GitHub Release:** 3/3 assets verified

## Downloads

| File | Description |
|------|-------------|
| [audit_report_eth_path2.json](evidence/redteam-audit-2026-05-08/audit_report_eth_path2.json) | Full audit report (JSON) |
| [ans104_extraction_report.json](evidence/redteam-audit-2026-05-08/ans104_extraction_report.json) | ANS-104 bundle extraction |
| [trinity_full_redteam_audit.py](scripts/redteam-audit/trinity_full_redteam_audit.py) | Audit script |

## Evidence

- [Evidence README](evidence/redteam-audit-2026-05-08/)

---

*Audited 2026-05-08.*
