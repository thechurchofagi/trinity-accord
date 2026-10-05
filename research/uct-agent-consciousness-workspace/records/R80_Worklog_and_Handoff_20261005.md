# R80 — Worklog and handoff

Date: 2026-10-05. Continuing remote head `2c35a3bd2b7e92065d3f63c80959c22219c891dc` on the existing UCT research branch. Current HANDOFF.md, MASTER_INDEX.md, AGENTS.md and WORKLOG.md were read. R79's preserved analysis and code, the R78 training code, source checkpoints, and UCT I sections 3.5, 6.3 and 9 were inspected. Published A/B/C and integrated manuscript v0.3 remain unchanged.

## Completed sequence

1. Distinguished whole-vector input recoverability from preservation of constituent-local causal organization. Derived the inverse for a nonsingular tanh encoder and proved the obstruction to constituent-local bijections when single-input units become jointly dependent.
2. Combined R78's loss inequality with its affine consumer to obtain a restricted necessity result: loss below log(2) requires at least one used joint hidden route. The affine-consumer premise is essential.
3. Executed all initial/final checkpoints of all 16 archived runs: 1,024 activation replacements and 256 input-flip clamps. These are deterministic software evaluations, not new training or independent experimental subjects. Results include every patch and route effect.
4. Found that all eight full-training models retain distinct finite input codes, but change from 2 to 4 effective input dependencies and from 2 to 4 distinct values per hidden unit. Their joint routes are used by the actual affine readout. The six task failures remain failures. Frozen-hidden controls preserve their encoder; their readout changes.
5. Tested limits: unused readout despite encoding, odd dense encoders without mixed contrast, nonlinear consumer solving the task without mixed hidden units. All scope checks passed. Maximum patch discrepancy 4.25e-15; inverse numerical error 2.80e-8. Saturation prevents treating the inverse check as unlimited physical precision.
6. Reviewed direct causal-abstraction precedents at the scopes listed in the report. Do not claim novelty for probing-versus-use, interchange intervention, invertibility, or port-preserving maps.

## Failures and corrected interpretations

More dependence is insufficient for the target relation; a used joint route is insufficient for perfect accuracy; better performance need not change hidden organization if the consumer is nonlinear. Exact information recovery does not establish old local organization, robustness or an installed decoder. Changing nonzero weight support is not adding physical wiring. The whole initial model already had a common consumer. No recurrent inference memory, self-maintenance or fear was acquired by this architecture.

No tool failure or failed assertion occurred in the R80 computation. The analysis was rerun after adding the two analytic scope counterexamples. There were no new optimization attempts and no excluded checkpoints. Source reading used primary papers; no third-party full text is in the package.

## Conclusion and next step

Positive limited result: recoverability of all inputs and actual constituent reorganization can coexist. C1 interprets verified actual relations conditionally, with token and complete K specified; this is not empirical confirmation of C1 or a scalar experiential increase. Internal access remains irrelevant to experience existence within the premises. Major-breakthrough status: not met.

Next audit the earlier R65 core-preservation construction before developing a small relation-preserving extension versus replacement. Require actual preservation of updates, ports and old consumer, and address feedback/shared resources. Do not return to another noise grid or self-report benchmark. Use the present report and `R80_Research_Package_20261005.zip`; the ZIP preserves input relative paths and full results.

Storage: direct research-branch commit with [skip ci], update HANDOFF.md and MASTER_INDEX.md together, nonforce update, lightweight confirmation. No publication, PR, CI or deployment action.
