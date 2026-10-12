# Validation

- `python3 check_role_automorphism.py --write EXACT_RESULTS.json`: PASS; 64 structures; 8 swap automorphisms; 56 non-automorphisms; 16 invariant and 16 reversing target pairs on true-automorphism structures; parameter transport covariance PASS.
- `python3 audit_map.py <root> <restored map>`: PASS; effective 913 nodes, 424 rules, 261 context links; 0 unresolved deductive references; 0 cycles; 0 empty/non-list `all_of`.
- JSON parsing: required for all new and changed JSON before commit.
- Formal promotion: none; `MAP_EXTENSION.json` records 0/0/0 and disabled status.
- Mathematical scope: definability-to-invariance is standard; the finite checker verifies only the declared witness counts. No converse, actual installation, phenomenal identity or full historical semantic proof is claimed.
- Inherited `records/NAV20261010_Map_Integration/validate_current_map.py`: FAIL at its obsolete `latest_work_log == latest_research.work_log` assertion. Disabled follow-ups are synchronized under `latest_followup_application`, while the old validator compares against the formal `latest_research`; A5E does not rewrite historical integration semantics merely to obtain a green check. JSON parsing and the current follow-up registries were checked directly.
