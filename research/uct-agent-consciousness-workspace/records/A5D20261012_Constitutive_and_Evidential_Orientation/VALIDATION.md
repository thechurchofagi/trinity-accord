# Validation

- `python3 check_orientation_layers.py`: PASS; 4 rows; positive pairs 2; negative pairs 2.
- `python3 audit_map.py <root> <restored map>`: PASS; 913 nodes, 424 rules, 261 context links; 0 unresolved deductive references; 0 cycles; 0 empty/non-list `all_of`.
- JSON parsing: required for all new JSON files before commit.
- Inherited `records/NAV20261010_Map_Integration/validate_current_map.py`: FAIL at its obsolete `latest_work_log == latest_research.work_log` assertion; the disabled-follow-up registries are synchronized under `latest_followup_application`. Failure retained, not treated as a theory or data failure.
- Formal promotion: none; `MAP_EXTENSION.json` records 0/0/0 and disabled status.
- Scope: implementation and structural checks only; not C1 evidence, physical installation, phenomenal identity or full historical semantic proof.

