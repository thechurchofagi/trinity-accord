# R202 whole-map compatibility audit

Authoritative base: UCT-MAP-v1.1.2, graph SHA256 `0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612`, review ledger SHA256 `0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687`.

The restored complete graph contains 913 nodes, 424 active conditional rules, 261 contexts and 10 suspended historical rules; all 1,608 review items were loaded. The disabled R202 candidate contributes 10 nodes, 4 rules and 5 contexts. All 20 checks in `MAP_COMPATIBILITY_AUDIT.json` pass: references resolve, IDs do not collide, the combined rule graph is acyclic, every rule uses simultaneous `all_of`, same-instance bindings and proof/alternative fields, C1 remains axiomatic, basal experience is not gated, report limits persist, and actual use is distinct from evidence.

Joint satisfiability was reviewed: prospective ignorable auditing, informative independently calibrated endpoint error, conditional nondifferentiality, positivity and actual-use separation can hold together but none follows from another. Their truth remains empirical. Structural compatibility is not semantic adoption, premise truth, actual application, reviewer closure or global proof.
