# R131 validation record

6 October 2026. General proofs were checked manually, not by a proof assistant.

- validate_formal_map.py: 110 checks passed; 249 nodes, 112 rules; all prior 236 nodes/106 rules preserved field-for-field, all four published source snapshots retain exact byte counts/SHA-256/Git blob identities, case references resolve and every explicit scope is rendered.
- check_probe_theorems.py: 50 exact rational checks passed, including 100 probability-law pairs for the inverse-norm envelope. Checks cover the binary marginal null direction, a joint-probe repair, a controlled hidden-bit nonclosure witness, the specified decision gap and rank boundary examples n=2 through 8.
- General proof scope: all probability laws on a declared finite outcome set and exact fixed expectation probes. Restricted model classes, statistical estimation, physically supported interventions and full experiential identification are separate obligations.
- Historical review scope: all X01–X38 case sections and the 47-family table were read; selected PLT sections were inspected. The full historical ledger and its old scripts were not exhaustively re-audited or rerun. No raw thousands-entry total is certified.

## Execution issues preserved

The initial check program used SymPy. Both the default and supplied primary-runtime Python lacked that dependency, so those two runs stopped at import before testing any mathematical assertion (ModuleNotFoundError: sympy). The initial program is retained as check_probe_theorems_sympy_attempt.py. The final check uses only Python's standard-library Fraction and exact row reduction; it completed successfully. No dependency was installed. A file-replacement patch was rejected because delete/add targeted the same path in one patch; no content was changed by that rejected patch, and the subsequent ordinary rewrite succeeded.

No new empirical experiment, training, publication or DOI release was performed. Structural checks do not certify all physical premises or historical novelty.
