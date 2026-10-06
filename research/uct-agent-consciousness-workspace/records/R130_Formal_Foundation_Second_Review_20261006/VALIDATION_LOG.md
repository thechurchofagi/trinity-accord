# R130 validation record

Final current-state graph/source check: **99 checks passed**, **236 nodes / 106 rules**. All four fixed paper byte counts, SHA-256 hashes and Git blob identities remain unchanged. Every R129 node/rule ID is retained. Exactly two node records and one rule are amended for F20. All 13 existing node scope fields now appear in the readable ledger (F21). The per-rule matrix covers all 106 rules and marks nine B target-specific bridges as scope/dependency review rather than independent source-theory verification.

Commands:

```
python records/R130_Formal_Foundation_Second_Review_20261006/check_review_boundaries.py
python records/R130_Formal_Foundation_Second_Review_20261006/validate_formal_map.py
```

The fair-mask witness has marginal internal TV=0, common-b conditional TV=1, joint-cut TV=1 and output TV=1, with zero decoding errors. It rejects the unqualified marginal reading and supports retaining the original common-b or joint-cut premise.

The deterministic check covers 27 total maps on three states and 64 pairs of binary summaries: **1,728** cases. Of these, **840** have both summaries individually closed; all have joint closure on the actual image. This finite stress check is not a proof for arbitrary state sets; the general proof remains coordinatewise substitution.

The finite decision check covers **243** cases: 81 two-context/two-action payoff tables at three positive rational context weights. There are 189 zero-gain cases, 54 strict-gain cases and 135 cases with at least one conditional tie. Nonnegative optimal value and the common-optimum equality condition pass throughout. These are exact rational calculations, not sampled data or training.

Execution history: the first R130 source-check invocation stopped because one inherited D snapshot path still pointed to the new record directory. The actual unchanged D sources remain in R129. That reference was corrected without changing source bytes or weakening assertions. The next run passed 98 checks; after the F21 ledger-export assertion was added, the final run passed 99. No failed mathematical case was removed.

The archive is a review/continuation snapshot, not a publication or a complete dataset backup. Its package manifest lists exact included paths, byte counts and SHA-256 values. GitHub saves use an expected-head lease and remote blob readback. No new experiment, empirical interpretation, proof-assistant certification, DOI/release or CI is implied by successful storage.
