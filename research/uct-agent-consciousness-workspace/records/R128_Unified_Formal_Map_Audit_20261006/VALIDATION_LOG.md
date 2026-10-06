# R128 validation record

The first graph/source validation reached the source checks and failed B's exact byte-count assertion: the local copied Markdown had acquired one terminal newline (59,959 bytes instead of 59,958). This was a copy-format issue, not a theorem or published-source change. The extra byte was removed. The second run passed all 51 graph/dependency/source checks, including all three original Git blob identities and publication-record SHA-256 values.

Final source-staging inspection found the same extra terminal newline in three supplementary snapshots: A's original graph, A's original audit and B's historical map. Those copied files were restored to the exact source bytes and checked against their original Git blob IDs. B's current ledger and all three publication records also match the originals. These source-copy checks are recorded separately in SUPPLEMENTARY_SOURCE_CHECK.json; they do not add theorem validation claims.

The exact joint-closure checker passed using rational arithmetic on eight states and sixteen nonzero transition entries. It retained both the failed all-state joint closure and successful four-state invariant-domain restriction. No random sampling, training or empirical inference occurred.

Commands, from the workspace root:

```bash
python records/R128_Unified_Formal_Map_Audit_20261006/validate_formal_map.py
python records/R128_Unified_Formal_Map_Audit_20261006/check_joint_closure.py
```

These outputs validate the stated graph constraints, source identity and finite witness. They do not certify all proof sketches or physical premises. Manual review scope is in UCT_FORMAL_AUDIT.md. Storage readback is separate; no research rerun is required merely to commit these files.
