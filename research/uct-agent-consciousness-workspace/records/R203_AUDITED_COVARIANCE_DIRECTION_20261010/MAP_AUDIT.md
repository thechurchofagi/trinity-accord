# R203 whole-map compatibility audit

Authoritative base: UCT-MAP-v1.1.2, graph SHA256 `0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612`, review ledger SHA256 `0513cb55cef94d82adcaea46af1974438a424aeba152f4c9d5655340f9271687`.

The release capsule restored and verified all 82 members. The completed graph contains 913 nodes, 424 active rules, 261 nondeductive contexts and 10 suspended historical rules; all 1,608 review items were loaded. The disabled R203 candidate contributes 10 nodes, 4 rules and 5 contexts. All 22 structural checks in `MAP_COMPATIBILITY_AUDIT.json` pass. `WHOLE_MAP_COVERAGE.json.gz` records stable IDs and content hashes for every one of the 1,598 completed nodes/rules/contexts, while explicitly marking inherited proofs as not newly reproved.

Node concepts, quantifiers and scopes were checked; every new rule keeps its `all_of` premises simultaneous and binds the same validation domain, bearer class, interval, complete signature and actual-use stratum. The combined dependency graph is acyclic. C1 remains axiomatic, U1 is not gated, report-domain limits persist, and actual route use remains distinct from audit, telemetry, bypass and confidence evidence.

Joint satisfiability is conditional: one nondegenerate latent target, positively oriented endpoint, bounded within-target residual, fixed-sample independent audit and actual-use stratum can coexist, but none is inferred from another. The exact dependent-error twin shows why endpoint/marker association alone cannot discharge the residual premise.

Affected rederivation is limited to R202 calibration/interface statements, R157 report/transport and R173 use/retention. R202's algebraic inversion remains conditionally valid; its endpoint-class residual test and unqualified bypass rejection are narrowed. Typed nondeductive source/module anchors are not treated as missing node premises. Structural PASS is not a new semantic proof of the completed map, premise truth, endpoint validation, residual-bound evidence, actual application, familiar-continuity attribution, `V→T` transport, reviewer closure or activation. R203 remains disabled; no completed-map version increment is justified.
