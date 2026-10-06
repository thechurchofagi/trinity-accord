# R129 validation record

6 October 2026. Both commands completed successfully:

```
python records/R129_Four_Paper_Integration_20261006/validate_formal_map.py
python records/R129_Four_Paper_Integration_20261006/check_exact_models.py
```

The graph/source validator passed **91 checks**, with **236 nodes and 106 rules**. It verifies unique/resolved IDs, acyclic rule dependencies, preservation of all R128 node/rule contents, all four pinned paper hashes, nine new exact source snapshots, D paper/audit/claims against the publication manifest, retention of all original D definitions/claims/context edges, selected forbidden dependency paths, and the attribution amendment.

The exact-model check enumerates all **243** coefficient profiles. Two bundled logits give 43 signatures (largest class 17); five calibrated logits identify all 243. Five deterministic signs give 121 signatures (largest class 9), so these observations cannot be silently substituted for calibrated logits. Two bundled signs give nine signatures (largest class 46).

The rational four-world construction verifies valid binary potential outcomes, unchanged O, monotone Q response, matched action marginals and reversed optimal decisions. Optimal marginal-only value is **5/8**, informed value **3/4**, difference **1/8**. Context-blind randomization cannot improve the marginal-only value by linearity.

General mathematical proofs are reviewed manually in R129_Integration_and_Proof_Audit.md. These checks do not prove every natural-language theorem, all physical premises, source-theory fidelity, or exhaustive coverage of every sentence. The graph is not proof-assistant certification. Prior neural/agent experiments were not rerun; R128's unchanged stochastic counterexample was not unnecessarily rerun for storage. No training, new empirical measurement, publication or CI was initiated.

Source transfer preserved UTF-8 bytes and terminal newlines exactly. All nine new snapshot Git blob identities passed on the first completed validation. A/B/C hashes remain unchanged. Publication and preservation fields in copied records are historical, not newly asserted external status.
