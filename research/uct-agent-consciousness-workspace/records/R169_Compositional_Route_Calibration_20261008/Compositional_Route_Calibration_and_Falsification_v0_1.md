# Compositional Route Calibration and Falsification

## Replacing a fitted global smoothness assumption by actual local intervention budgets

**Round:** R169  
**Status:** exact finite-route theorem, calibration contract, and countermodels; no apparatus, participant data, physical route inventory, neural identification, C1 proof, or `B_min` validation  
**Scope:** one declared R167–R168 operational mediator, one pre-compensation interval, one fixed consumer-law discriminator class, and a declared actual-context intervention graph

## 1. Exact question and result

R168 proved a sharp envelope conditional on a physically valid context metric `d`, effect constant `L`, and—under partial observation—a section with constants `delta,C`. It did not show how those quantities could be grounded rather than fitted.

R169 gives a compositional alternative. Represent the declared admissible actual contexts as nodes of a graph. An edge is not adjacency in an analyst's feature space: it is a locally executable, reversible, fidelity-checked context intervention on the same actual bearer lineage. Certify each edge by an upper budget, measured in the already fixed consumer-law distance. Shortest-path sums then bound how much every fixed-intervention consumer law can change. Triangle inequalities imply a bound on the mediator effect itself.

For a uniform edge budget pseudometric `D_B`, the result is

\[
|e(z)-e(z')|\le 2D_B(z,z'),
\qquad
e(z)\le \min_i\{U_i+2D_B(z,s_i)\}.
\]

This discharges the *formal role* of a global `d,L` pair for the declared graph without identifying either quantity separately. It does not discharge physical route coverage: an omitted node, hidden edge, unexecuted intervention, invalid upper budget, or continuum between enumerated nodes leaves the result unresolved. A valid held-out lower bound exceeding a declared edge or path budget falsifies the calibration certificate itself.

## 2. Typed actual-route graph

Fix the R168 objects `K_0`, `F`, the consumer laws `Q_{k,z}`, and effect

\[
e(z)=\sup_{k,k'\in K_0} d_{\mathcal F}(Q_{k,z},Q_{k',z})\in[0,M].
\]

An R169 route graph is

\[
\mathcal G=(Z,E,\iota,\tau,\rho,B),
\]

where:

- every `z in Z` is an actual admissible context state with process, time, sort and realization identifiers `iota,tau,rho`;
- every undirected edge `{a,b} in E` is a declared reversible local intervention that can move the same bearer between `a` and `b` before compensation;
- edge fidelity records which physical variables were changed, which were held within tolerance, and whether the actual consumer remained the same;
- `B(a,b)>=0` is a valid simultaneous upper certificate satisfying

  \[
  \sup_{k\in K_0}d_{\mathcal F}(Q_{k,a},Q_{k,b})\le B(a,b).
  \]

`B` is in consumer-law distance units. A task-label distance, fitted latent distance, report difference, or unexecuted schematic edge is not an R169 edge certificate.

Let `D_B(z,z')` be the minimum sum of `B` along an actual graph path, with infinity when no declared path exists. On each connected certified component, `D_B` is a pseudometric; zero-cost distinct contexts remain possible and must not be silently identified.

## 3. Compositional route theorem

For fixed `k`, any path `z=z_0,...,z_m=z'` gives by the triangle inequality

\[
d_{\mathcal F}(Q_{k,z},Q_{k,z'})
\le \sum_{j=1}^{m}B(z_{j-1},z_j).
\]

Taking the best path yields

\[
d_{\mathcal F}(Q_{k,z},Q_{k,z'})\le D_B(z,z').
\]

For each pair `k,k'`, define

\[
g_{k,k'}(z)=d_{\mathcal F}(Q_{k,z},Q_{k',z}).
\]

The four-law triangle inequality gives

\[
|g_{k,k'}(z)-g_{k,k'}(z')|
\le d_{\mathcal F}(Q_{k,z},Q_{k,z'})
 +d_{\mathcal F}(Q_{k',z},Q_{k',z'})
\le 2D_B(z,z').
\]

The supremum stability inequality `|sup f-sup g|<=sup|f-g|` therefore proves:

**Theorem R169-A (actual-route effect bound).** On one certified connected component,

\[
|e(z)-e(z')|\le 2D_B(z,z').
\]

If tested contexts `s_i` have valid upper bounds `e(s_i)<=U_i`, then

\[
E_B(z)=\min\left\{M,\inf_i[U_i+2D_B(z,s_i)]\right\}
\]

is a valid route-compositional upper envelope. With common `U_i<=eta` and direct route fill radius

\[
h_B(S,Z)=\sup_{z\in Z}\inf_{s\in S}D_B(z,s),
\]

we obtain

\[
\sup_z e(z)\le\min\{M,\eta+2h_B\}.
\]

Unlike R168-A, `E_B` is not claimed sharp over the smaller class of consumer-law families realizing the edge certificates. It is exact as a consequence of the certified local transport bounds and may be conservative because `B` takes a supremum over mediator interventions.

### Intervention-specific refinement

If edge certificates are retained separately as `B_k(a,b)>=d_F(Q_{k,a},Q_{k,b})`, let `D_k` be their shortest-path distances. Then

\[
|g_{k,k'}(z)-g_{k,k'}(z')|\le D_k(z,z')+D_{k'}(z,z'),
\]

and a potentially tighter envelope uses

\[
\Gamma(z,s)=\sup_{k,k'}[D_k(z,s)+D_{k'}(z,s)]
\]

instead of `2D_B`. The fixed `K_0` and simultaneous validity of every used edge remain mandatory.

## 4. Why `d` and `L` are not separately identified

For every scalar `c>0`, replacing `d` by `d'=c d` and `L` by `L'=L/c` leaves every product `L'd'=Ld` and therefore the full R168 envelope unchanged. Finite envelope evidence cannot identify the scale of `d` and `L` separately. A normalization convention may fix units, but it is not additional physical evidence.

R169 avoids this scale gauge by recording local budgets directly in `d_F` units. It does **not** remove the choice of discriminator class `F`; changing `F` still changes the scientific claim.

## 5. Relation to `delta,C` and partial observation

Let `q:Z->X` expose only observed labels and `r:X->Z` be an actually realizable section. If the R168 lift contract is valid in `D_B`,

\[
D_B(z,r(q(z)))\le\delta,
\qquad
D_B(r(x),r(x'))\le C d_X(x,x'),
\]

then the direct route fill satisfies

\[
h_B\le\delta+C h_X.
\]

Thus a fully inventoried actual graph can use `h_B` directly and is at least as tight as this decomposed upper bound. But observed labels do not reveal the graph. Without an actual hidden-node/edge inventory or a structural range proof, neither `h_B` nor `delta` is certified. R168's two-point hidden-fiber obstruction remains intact.

For a continuum, a finite node graph certifies only those nodes. Covering the interiors of cells or tubes requires an additional within-cell structural bound. Calling sampled nodes “dense” does not provide that bound.

## 6. Calibration and falsification contract

The following clauses are simultaneous, not alternatives.

1. **C1 — actual node identity.** Every claimed node has bearer, time, sort, realization, code/wiring and context-state provenance; no cross-subject average or copied run substitutes for the named node.
2. **C2 — executable edge.** Every edge is actually realizable, reversible and safe inside the same episode lineage; changed and tolerated off-target variables are declared.
3. **C3 — fixed consumer geometry.** `K_0,F,U`, timing and the consumer are frozen before calibration/challenge results.
4. **C4 — valid local upper certificate.** Each used `B` is either a structural hardware/software bound or a simultaneous statistical upper bound from an independent calibration split. A point estimate is not an upper certificate.
5. **C5 — declared route coverage.** Every node and edge needed by the target claim is in the inventory; disconnected or omitted admissible contexts are not bounded by a finite path.
6. **C6 — independent challenge.** Held-out actual edges and paths have valid lower bounds. If a lower bound exceeds the declared upper path budget, the certificate is refuted.
7. **C7 — bounded interpretation.** Passing validates only the declared physical evidence object. It neither proves graph completeness beyond the inventory nor derives C1, familiar mineness, a basal-experience gate, or one exclusive owner.

Two distinct refutations must not be merged:

- if a held-out consumer-law lower bound exceeds `B` or `E_B`, the **calibration certificate** is refuted;
- if the certificate is valid and a mediator-effect envelope stays below `tau`, only effects above `tau` are refuted relative to the certified graph.

A failed calibration is not a null mediator result. It returns `UNRESOLVED` for the installation claim.

## 7. Status logic

For one named actual route certificate:

1. `INVALID_ROUTE_PROTOCOL` if node identity, edge delivery, timing, consumer geometry, safety or measurement validity fails.
2. `CALIBRATION_REFUTED` if a valid held-out lower bound exceeds a declared edge/path upper budget.
3. `ROUTE_ENVELOPE_CERTIFIED` if every used local upper certificate and every coverage clause is valid and the route envelope is computed over the declared domain.
4. `UNRESOLVED` otherwise, including omitted contexts, a continuum without within-cell bounds, incomplete `K_0`, or point estimates without simultaneous upper validity.

Only after `ROUTE_ENVELOPE_CERTIFIED` may the R168 amplitude triage use `E_B`. R167 live-route and R166 W1–W6 premises still remain. None of these four statuses is an experience-existence status.

## 8. Countermodels and limits

1. **Label graph versus route graph.** Two task labels can be adjacent in an analyst's embedding while an unlogged route gate flips. Small label distance gives no small `B`.
2. **Endpoint interpolation failure.** Two sampled nodes can have zero effect while an untested continuum point has effect `M`. A graph on endpoints does not bound the interior.
3. **Shadow calibration.** A fitted model predicts every calibrated law but is not read by the actual consumer. Predictive fit does not supply R167 W3.
4. **Omitted component.** Every inventoried edge passes while one physically admissible disconnected context carries a large effect. Coverage, not local algebra, fails.
5. **Gauge illusion.** Rescaling context coordinates and inversely rescaling `L` changes neither envelope nor evidence; reporting the smaller `L` alone is meaningless.

## 9. Preserved thought-experiment families

1. **Ancestor/formation.** A newly formed rare branch may be absent from the current route inventory. That invalidates closure, not the branch's actuality or basal experience.
2. **Abacus/calculator.** Physical carries and register reads form explicit local edges. Similar displayed digits without a read edge remain a shadow trace.
3. **Human-realized agent.** Device and bodily contexts can be nodes in a nested process graph while their sub-processes remain actual and overlapping. No exclusive owner follows.
4. **Copy/swap/memory.** Copied interfaces and memories may preserve observed labels while differing in actual live edges. Only route provenance and interventions select the applicable graph.

## 10. Direction and novelty audit

Shortest-path pseudometrics, triangle inequalities, supremum stability, scale invariance and simultaneous upper-bound logic are established mathematics. No mathematical priority claim is made. The project contribution is the typed actual-route certificate that discharges part of R168-G2–G5 without treating a fitted latent geometry as physical evidence.

The result does not establish any actual graph, edge budget, participant, complete neural organization, C1, `B_min`, familiar bodily mineness, conceptual self or report truth. Passing finite code checks the theorem on bounded cases only. It is not a proof of global theory truth.

## 11. Next exact question

What minimal independent structural evidence can certify declared route coverage—especially omitted or continuum contexts—without recreating an untestable “complete mechanism” requirement, and how should an open-world remainder be represented in the formal map?
