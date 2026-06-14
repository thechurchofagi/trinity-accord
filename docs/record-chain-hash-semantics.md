# Record-Chain Hash Semantics

## Overview

The Record-Chain uses SHA-256 hashes for continuity and integrity verification.
However, the hash semantics are nuanced — `record_sha256` is **not** the same as
the raw file SHA-256 of the record JSON.

## `record_sha256` — Append-Declared Continuity Hash

The `record_sha256` field in each record is the **append-declared continuity hash**.
It is computed and assigned during the record-chain append process and stored in
the record file and the record index.

**It is not currently promised to equal the raw file SHA-256.**

This is because record files contain self-referential fields (like `record_sha256`
itself) and append-assigned fields (like `record_id`, `assigned_at`, etc.) that are
added after the hash is computed.

## Hash Variants

The verifier script (`scripts/verify_native_record_hash_semantics.py`) computes
the following hash variants for each record:

| Variant | Description |
|---|---|
| `raw_file_sha256` | SHA-256 of the raw record file bytes |
| `full_canonical_sha256` | SHA-256 of canonical JSON of the full record |
| `without_record_sha256_canonical_sha256` | Canonical JSON excluding the `record_sha256` field |
| `without_append_fields_canonical_sha256` | Canonical JSON excluding all append-assigned fields |
| `declared_record_sha256` | The `record_sha256` value declared in the record file |
| `signed_payload_sha256` | The `signed_payload_sha256` from `authorship_proof` |

## Continuity Verification

The verifier checks:

1. **Index consistency**: Each record's declared `record_sha256` matches the value in `record-index.json`
2. **Chain continuity**: Each record's `previous_record_sha256` matches the previous record's declared `record_sha256`
3. **Chain-tip consistency**: The latest record's declared `record_sha256` matches `chain-tip.json`

## Usage

```bash
python scripts/verify_native_record_hash_semantics.py --base-dir .
python scripts/verify_native_record_hash_semantics.py --base-dir . --out report.json
```

## Contract Test

```bash
python scripts/test_native_record_hash_semantics_contract.py
```

This runs the verifier and fails if any declared continuity mismatch is found.
