# Validation record

- `check_sign_anchor.py`: semantic JSON equality with `EXACT_RESULTS.json`; verifies the two full observable tables, 4/2/1 orientation counts and different route-swap orbits for 4-edge joint versus 2-edge distributed mappings.
- `audit_map.py`: fresh effective-graph restoration and traversal; 913 nodes, 424 active rules, 261 context links; zero unresolved deductive references, cycles, empty `all_of` or non-list `all_of`.
- JSON parse: all A5C JSON artifacts parse successfully.
- Inherited `validate_current_map.py`: expected exit 1 at its integration-era assertion equating `latest_work_log/latest_handoff` with `latest_research`; later follow-up applications intentionally use a separate `latest_followup_application` pointer. The failure is preserved and not treated as a scientific failure or silently repaired.
- Scope: executable checks validate the declared finite objects only. They do not validate C1, actual physical installation, `H_pc`, report reliability or full historical semantics.

