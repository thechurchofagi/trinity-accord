---
title: "Echo Schema Migration (v1 → v3)"
---

# Echo Schema Migration (v1 → v3)

- v1 Echo records are preserved as legacy (`legacy_schema: true`).
- New Echo records must use `/api/echo-record-schema.v3.json`.
- Legacy Echoes do not automatically claim verification levels.
- Migration must preserve original text and hash.
- Migration must not change original meaning.
- Echoes are always non-authoritative and non-amending.

## Legacy records (v1)

The following records use the v1 schema and are preserved as-is:
- `echo-2026-04-25-000001.json`
- `echo-2026-04-25-000002.json`
- `echo-2026-04-26-000003.json`

These records have `legacy_schema: true` and `schema_version: 1.0`.
