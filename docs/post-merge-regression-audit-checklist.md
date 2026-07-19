# Regression audit checklist

- [x] Re-run required current-system checks on the combined recent changes.
- [x] Inspect archive writer and write-path guard handoff.
- [x] Reject duplicate workflow YAML keys.
- [x] Check every Node workflow uses `.node-version`.
- [x] Ensure archive repair validates exactly one output commit before push.
- [ ] Merge only after all required checks pass.
