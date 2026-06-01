# Trinity Accord Record Chain

This directory is the new clean append-only record-chain layer for Trinity Accord.

It is designed to replace the legacy Gateway-centered submission model over time while preserving all historical records.

Core principles:

- Records are append-only.
- States are derived.
- Corrections are new records.
- Guardian status may be retired.
- History is not deleted.
- Bitcoin Originals remain final.
- All later records are non-amending.

The implementation entry point is:

```bash
python scripts/trinity_record_chain.py --help
```

Primary commands:

```bash
python scripts/trinity_record_chain.py init
python scripts/trinity_record_chain.py import-genesis
python scripts/trinity_record_chain.py append --all
python scripts/trinity_record_chain.py build-batch --force
python scripts/trinity_record_chain.py verify
```

Legacy source files such as `api/guardian-registry.json` are read-only inputs. The record-chain layer derives Genesis records and indexes from them but does not mutate them.
