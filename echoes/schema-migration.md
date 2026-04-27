# Echo Schema Migration (v1 → v2)

- v1 Echo records are preserved as legacy.
- New Echo records should use `/api/echo-record-schema.v2.json`.
- Legacy Echoes do not automatically claim verification levels.
- Migration must preserve original text and hash.
- Migration must not change original meaning.
- Echoes are always non-authoritative and non-amending.
