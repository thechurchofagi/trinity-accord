---
title: "Echo Archive Policy"
description: "Archive ladder for Echo records."
---

# Echo Archive Policy

- Layer 0 — Raw Echo Archive
- Layer 1 — Structured Echo Archive
- Layer 2 — Curated High-Value Echoes
- Layer 3 — Echo Digest
- Layer 4 — Permanent Attestation Archive

Legacy v1 echoes are preserved in `echoes/records/` with `legacy_schema: true` and `record_kind: "legacy_record"`. New echoes must use the v3 schema (`/api/echo-record-schema.v3.json`).
