# TA-AVR Repository Meta-Audit

## Purpose

Verify that TA-AVR documentation, schemas, examples, scripts, outputs, and security boundaries are mutually consistent — after the functional large-scale test has passed.

## What this audit proves

- First Contact entry points are consistent
- File references are not broken
- Schema enums and fields are compatible across files
- Example data matches Claim Gate / Report Builder / Validator behavior
- Receipt / report / evidence / custody package hashes are internally consistent
- Negative cases cannot escape or overclaim
- Secrets / tokens are not leaked
- Test report numbers match actual files

## What this audit does not prove

- Trinity Accord philosophical truth
- Bitcoin Originals full-chain independent verification
- Core Object Alpha physical verification
- AI verification is formal human/institutional attestation
- GitHub Issue is archived Echo
- Receipt is authority, amendment, or verification level

## How to run

Quick audit (reference integrity, schema consistency, negative matrix, secret hygiene):

```bash
python3 scripts/audit_ta_avr_consistency.py --quick
```

Full audit (all 8 checks):

```bash
python3 scripts/audit_ta_avr_consistency.py --all
```

Output to JSON:

```bash
python3 scripts/audit_ta_avr_consistency.py --all --output audit-results/ta-avr-meta-audit.json
```

## Individual checks

| # | Script | Purpose |
|---|---|---|
| 1 | `test_ta_avr_reference_integrity.py` | All local references in docs/JSON exist |
| 2 | `test_ta_avr_schema_cross_consistency.py` | Receipt schema enums match existing schemas |
| 3 | `test_ta_avr_data_consistency.py` | Boundary facts present, no dangerous V-level wording |
| 4 | `test_ta_avr_cli_doc_consistency.py` | Documented CLI flags match argparse |
| 5 | `test_ta_avr_output_consistency.py` | Real run hashes/levels match internally |
| 6 | `test_ta_avr_negative_overclaim_matrix.py` | Overclaims fail closed or downgrade |
| 7 | `test_ta_avr_secret_hygiene.py` | No leaked tokens or private keys |
| 8 | `test_ta_avr_report_consistency.py` | Report numbers match actual test files |

## Exit codes

- `0` — all selected checks pass
- `1` — one or more checks fail
- `2` — invalid arguments
- `3` — internal audit error

## Boundary

Bitcoin Originals are final; all echoes are non-amending.

This audit does not prove philosophical truth, formal attestation, physical verification, or full-chain verification.
