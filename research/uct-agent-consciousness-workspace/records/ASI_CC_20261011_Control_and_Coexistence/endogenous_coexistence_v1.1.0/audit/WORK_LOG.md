# ASI-CC-v1.1.0 work log — 2026-10-11

## Baseline and objective
User requested continued research and a paper draft. Read supplied v1.0.0 manuscript, research note, handoff, source code and prior-art audit; verified connected research-guide v2.3, v1.0.0 candidate index and current branch HEAD1c88e643dfd67585bd6a60cb440b11526bf11151. Formal map baselineUCT-MAP-v1.1.2 and publication coverageUCT-PUB-v1.0.33 retained; already-public PR6 DOI10.5281/zenodo.23295776 not recycled as a new contribution.

Specific missing case: old monotone authority closure cannot be treated as exact when permissions are consumed or revoked. Current permissions may also undercount persistent effects. Selected an actual service-restoration contract rather than just enlarging an attack graph.

## Actions and findings
- Formulated the two-sided authority/effect witness, with one exclusive token and either a simultaneous guard predicate or persistent disable latches. Both are faithful but different endpoint semantics.
- Read primary sources on agent quiescence/authority succession/subgoal mutation. They already distinguish revocation from rollback and preserve obligations, so those principles are not claimed as new. Reviewed Sagas primary abstract/report; network-calculus author PDF §1.4 and formula/figure pages; proactive-sharing and nonideal-clock primary sources.
- Derived the exact discrete delayed-recovery backlog identity and burst/rate/latency margin, stating its inherited network-calculus origin. Derived exact linear debt growth for repeated fresh-burst epochs at fixed recovery rate. Retained initial-debt carryover and noninterchangeable-resource counterexamples.
- Executed recovery_frontier.py:11664 independent queue/formula comparisons,11684 envelope checks,665 tight profiles,105 overload profiles,100 epoch-reset cases. PASS.
- Executed effect_escrow_demo.py:12configurations,24 actual child processes,144 observed rounds,119 actual service-disable database changes and119 rejected expired-token replays. Some variants still lose service, distinguishing correct revocation from repair. No-repair escrow and insufficient-headroom escrow defer work rather than claim full service success. False recovery receipts remain a failing control.
- Reran three original v1.0.0 scripts, with semantic matches excluding time/interpreter metadata. Old counts not added to new evidence.
- Wrote a self-contained12page English draft, Chinese handoff, new stable RAC claim ledger, prior-art and review scope, index and reproducibility package. Compiled twice and rendered all12pages; corrected a shared-counter cross-reference that called a lemma a theorem. No remaining missing-reference/overfull warning.

## Failures and qualifications
No final computational assertion failed in this revision. The first preliminary queue identity check passed and is not counted separately from the final grid. Text-layout cross-reference corrected before release. Search returned irrelevant Salem labor records for a broad Sagas query; discarded. Some primary works were read only at abstract/metadata level (recorded in PRIOR_ART_REVIEW.md). No theorem is considered globally first-priority. Only new scripts were executed twice for final reproducibility; baseline scripts once this turn. No hardware root independence, trained LLM motive, real human consent or phenomenal experience measured.

## Map and coverage
Local model/proof and interpretation checks performed. Full historical913/424/261 semantic audit and all-published-claim census NOT completed. New RAC nodes remain disabled/PENDING_MAP and published scientific bytes unchanged. Candidate coverage delta records inherited queue mathematics and old EAC/PR6 overlap. This is a manuscript draft, not a DOI operation.

## Next
Investigate heterogeneous protected services with shared restoration capacity and experimentally justified effect completion, not independent per-service repair promises that cannot hold jointly. Any actual coalition or policy change must preserve actual effect liabilities, not just identity labels. Separate liveness promises from on-schedule admission and independently justify recovery evidence.

## Final count reconciliation
A manually written experimental count said105 epoch-reset profiles; the executed loop and archived JSON contain100 (sum of2+3+4+5+6 choices, times5 epoch lengths). Corrected manuscript and handoff to100 before final delivery. Overload profiles remain105; computations and theorem statements were unchanged.
