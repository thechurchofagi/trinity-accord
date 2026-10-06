# R130 — Second review and durable four-paper foundation

6 October 2026. Baseline: `2e1d77748bc4a0db24c9068a68c8d110bae2b783`, branch `uct-agent-consciousness-workspace`, repository `thechurchofagi/trinity-accord`.

## 1. Verdict and exact scope

**The reviewed map is suitable as the continuing conditional research foundation after the clarification below.** No contradiction requiring withdrawal of the reviewed core arguments was found. One map-level premise omission and one readable-ledger export omission were repaired. This is not an assertion that every sentence in four papers has been formally proven, every physical premise established, or every rival theory faithfully reduced.

All **106 rule entries** were re-examined for statement, simultaneous premises, proof sketch and scope. The nine theory-specific B bridges received a dependency/scope review: their target-theory fidelity remains a stated obligation, not an independently completed nine-theory literature audit. The inventory remains **236 nodes / 106 rules**. There is no new theorem-count claim.

The pinned source editions remain A/I v1.2, B/II v1.1, C/III v1.0 and D/TA-TR-2026-24 v1.0. Published source bytes are unchanged. All four source hashes and the previously retained D source materials are checked. The initial remote HEAD matched the R129 baseline. No new DOI, publication, empirical run, training or deployment was initiated.

## 2. F20 — Restore common external conditions in the cut bound

The original R127 §4 proof explicitly fixes the same external information b and query q when comparing preparations x and x'. The unified map's shortened `R127:MEDIATION` label and `R127:P2` statement did not display that condition. Reading the isolated graph could incorrectly suggest a bound on the marginal internal cut state even when the downstream decoder also uses B.

The corrected statement is: for common b,q supported under both preparations, let

\[
\mu_x=P(C\mid x,b,q),\qquad
\mu_{x'}=P(C\mid x',b,q),
\]

and assume the common downstream kernel

\[
P(Y\mid x,c,b,q)=W_q(Y\mid c,b).
\]

If the correct outputs differ, with conditional errors \(\epsilon_{x,b,q}\) and \(\epsilon_{x',b,q}\), then

\[
\operatorname{TV}(\mu_x,\mu_{x'})
\ge 1-\epsilon_{x,b,q}-\epsilon_{x',b,q}.
\]

**Proof.** Passing either cut law through the same kernel cannot increase total variation. The event consisting of x's correct answer has probability at least \(1-\epsilon_{x,b,q}\) under x, and at most \(\epsilon_{x',b,q}\) under x'. Subtract, then apply contraction. A negative right-hand side gives only a trivial bound. If there is no common supported b, this particular conditional comparison is not defined.

If B is not fixed, use the **joint cut (C,B)** and the same downstream kernel on that joint state. Marginalizing away B is not justified merely because B is individually independent of X.

**Counterexample to the unqualified marginal reading.** Let X and B be independent fair bits, let C=X XOR B, and decode Y=C XOR B=X. Both marginal C laws are fair, hence

\[
\operatorname{TV}(P(C\mid X=0),P(C\mid X=1))=0,
\]

while the decoding errors are zero. Applying an unconditional internal-only bound would require \(0\ge1\), which is false. At either common b, the two conditional C laws are distinct point masses and have TV=1. The two joint (C,B) laws also have disjoint supports and TV=1. The original conditional theorem is intact.

This is the existing R127 fair-mask example used to audit a map abbreviation, not a newly discovered information theorem. The canonical graph amends exactly two existing nodes (`R127:MEDIATION`, `R127:P2`) and one existing rule (`r127_2`), preserves their IDs and records the amendment. All other rule/node contents remain unchanged; the complete R129 baseline is retained.

## 2.1 F21 — Preserve scope in the readable ledger

The graph already contained 13 explicit `scope` fields, but the R129 readable node ledger did not export them. R130 renders every such field and all remaining node metadata, including original IDs, evidence records and amendments. This is an export correction, not 13 new premises or a change to published theory. It prevents readers of the ledger from losing conditions already present in the graph.

## 3. Rechecked proof families

| Family | Rechecked argument | Premise/limit retained |
|---|---|---|
| A:C1 → C1-OI/W, U1 | Composition of tokenwise isomorphisms; nonempty distinguished carrier | C1 already contains the universal experiential commitment; this is no derivation from consciousness-free physics |
| A:U2, evolutionary routes | Equality of quotient-valued maps transfers continuity in one predeclared geometry | Does not supply a continuous physical path, a unique metric or increasing richness |
| A ontology, support, nonproduct and selector arguments | Actual-token admission, specified products, orbit closure and overlap | Actuality/common signature/witnesses explicit; no unique subject follows from connectivity |
| B translation | Structural induction over typed admissible expressions | Expressibility, BAC and theory-specific fidelity/residuals are not automatically established |
| B recurrence/enabling | Nontrivial SCC or self-loop; required return path; distinguish causal connectivity from Jacobian | Local gain/stability does not define experience existence |
| C:P1/P2 | Well-defined fixed J; contraposition and constancy on fibers | Set-level recovery need not be computable, continuous, stable or statistically estimable |
| C selection, Price identities and P6 | Reweighting/conditional expectations; row-sum closure with point-mass necessity | Finite fixed kernel, positive class weights, all initial laws; no population-history shortcut |
| C:P7 and D decision witness | Nonnegative conditional regret; common-optimum equality; fixed 1/8 example | Same action/payoff domain and unrestricted observation-wise policies; fitted performance may differ |
| C loss/TV and R127 information | Entropy/KL decomposition, TV contraction, conditional Fano bound | Fixed evaluation law, finite quantities, correct conditional or joint state, actual specified estimator error |
| R126 | Representative-independent quotient; half-diameter bound; finite stable refinement | Total same-label operations, output agreement, sufficient finite state; enabledness needed for partial operations |
| R128 | Deterministic coordinatewise closure; stochastic joint-law counterexample | Common operations/time/domain; joint image rather than assumed full Cartesian state space |
| D:F1/F2 | Rank deficiency versus explicit five-logit inversion | Fixed five-parameter model; calibrated logits and valid contrasts; choices alone do not identify coefficients |
| D payoff/Fréchet | Four binary payoff values determine four coefficients; probability nonnegativity gives sharp interval | Nonzero interaction can matter, but not every problem needs an explicit joint table; cross-action constraints may tighten bounds |
| D separability/grid envelope | Path cancellation; nearest-grid triangle inequality | Additivity does not fix response shape; a justified global regularity bound is required |
| D evidence/UCT interpretation | Distinguish source evidence, methodological ladder and conditional complete-type interpretation | No control-to-valence inference or new U1 gate; actual complete-type difference remains independently grounded |

The main source passages re-opened for close review were A §§2.5, 3.1–3.5 and the C1/U1/U2/U3/U0 section; B §§4.1–5.5; C §§5.1–5.3, 6.4 and 7.3; R126 §§4–6; R127 §§2–5 and actual-support discussion; R128 joint-state argument; and the R129 D integration proof record. Other branches were rechecked at the full current statement/premise/proof-ledger level with the previous source audit retained. External references and empirical datasets were not exhaustively reread or rerun. This is a single-assistant second review, not independent peer review.

## 4. Targeted mathematical verification

`check_review_boundaries.py` addresses three concrete risks:

1. An exact rational fair-mask construction distinguishes marginal, common-b conditional and joint-cut TV. This directly tests F20's failure mode.
2. All total deterministic maps on a three-state set and all pairs of binary summaries are checked for the common-operation joint-closure implication, including the actual joint image. This finite stress check supplements, but does not replace, the general coordinatewise proof.
3. All two-context/two-action payoff tables over {-1,0,1}, at three strictly positive rational context weights, check nonnegative optimal information value and the common-optimal-action equality criterion. This probes ties and zero-gain informative cases without sampling or fitting.

Graph/source verification also confirms the exact permitted amendments, retained IDs and source hashes, prohibited dependence routes, and coverage of the rule review matrix. Prior unchanged D and R128 exact-model results are retained; they need not be rerun solely for storage. None of these tests measures experience.

## 5. Durable continuation contract

The user's latest instruction is recorded in the root `MEMORY.md` and made a startup requirement in `AGENTS.md`. Handoff and index point to the R130 map/audit/proof ledger. This is an explicit project memory file; no claim is made that a hidden account-level memory service was modified.

Every later UCT step must start from the four-paper version-pinned map, attach to stable nodes, state all premises and the claim's type, supply proof/counterlimits and preserve provenance. Changed premises must be documented as amendments rather than silently rewriting history. Critical review remains allowed and required: “use this foundation” does not mean accepting a future error without correction.

Theory-first priority continues. New experiments require a sufficiently specified theoretical target and discriminating alternatives; experiment scores cannot substitute for missing deduction or actual-support grounding. Preserve weak/negative outcomes and existing uncertainty. T2 remains OPEN, C3 intervention transport NOT_TESTED and D's independent negative-valence bridge OPEN.

The next mapped theoretical problem remains payoff-relative sufficiency versus controlled dynamical closure and resource/time/port-compatible joint use. No unrelated theorem stack or new existence gate is introduced by this review.
