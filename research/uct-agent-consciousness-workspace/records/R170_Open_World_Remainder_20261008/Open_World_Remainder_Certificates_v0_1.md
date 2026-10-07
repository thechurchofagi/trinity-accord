# Open-World Remainder Certificates

## Sharp separation of amplitude, mean, and exceedance claims beyond a finite actual-route inventory

**Round:** R170  
**Status:** exact decomposition and impossibility theorems, finite-cell route lift, falsification contract and bounded checks; no apparatus, participant data, physical domain inventory, neural completeness, C1 proof or `B_min` validation  
**Scope:** one frozen R168 effect object, one R169 actual-route certificate, one declared target domain and one independently specified target measure where measure claims are made

## 1. Exact question and result

R169 bounded effects on nodes connected by certified actual intervention routes. It deliberately left omitted nodes and continuum interiors unresolved. R170 asks what can still be stated when that open-world remainder is retained rather than silently set to zero.

The minimal honest object is a decomposition of the declared target domain `T` into a certified covered part `C` and an unresolved remainder `U=T\C`. On `C`, R169 or a cell-to-anchor lift supplies a pointwise envelope `E_C`. On `U`, only the inherited range `0<=e<=M` is available. The sharp compatible pointwise envelope is therefore

\[
\overline E(z)=
\begin{cases}
E_C(z),&z\in C,\\
M,&z\in U.
\end{cases}
\]

This immediately yields three distinct conclusions.

1. If `U` is nonempty and no further amplitude premise is available there, the sharp global supremum bound remains `M`, even when `U` has arbitrarily small positive measure.
2. If a fixed target probability measure `mu` is independently justified, the sharp integral bound is

   \[
   \int_T e\,d\mu\le \int_C E_C\,d\mu+M\mu(U).
   \]

3. For any threshold `tau<M`,

   \[
   \mu\{e>\tau\}\le
   \mu\{z\in C:E_C(z)>\tau\}+\mu(U).
   \]

Thus a small unknown mass supports mean or exceedance-mass claims, never a nontrivial global-amplitude claim. These bounds are exact over the declared information class.

## 2. Typed target-domain and admission contract

Fix the R168 objects `K_0`, `F`, consumer laws `Q_{k,z}`, timing and

\[
e(z)=\sup_{k,k'\in K_0}d_{\mathcal F}(Q_{k,z},Q_{k',z})\in[0,M].
\]

An R170 target-domain contract is

\[
\mathfrak T=(T,A,\nu,\mathrm{id}),
\]

where:

- `T` is the claim's predeclared set of physically admissible context states, not the set observed after testing;
- `A` is an admission procedure or structural specification identifying which actual bearer/time/sort/realization states count as target contexts;
- `id` retains the R169 actual node identity fields;
- `nu` is absent for amplitude-only claims and is a fixed probability measure only for average or mass claims.

The domain may be finite, a physically range-bounded continuum, or a mixed space. A task label, analyst embedding, convenience sample or post-hoc list is not a target-domain proof. Claims about `nu` additionally require a sampling-frame or structural-measure justification; no canonical measure follows from the set `T` alone.

## 3. Certified cells and the explicit remainder

Let `V` be R169 certified anchor nodes. A certified cell `C_j` has:

- a physical admission predicate `A_j(z)` whose range is independently bounded;
- an anchor `v_j in V` with matching bearer lineage, sort and consumer;
- for every admitted `z`, an executable local route or structural channel certificate with budget `R_j(z)` in `d_F` units;
- a verified upper radius `r_j` satisfying `R_j(z)<=r_j` for all `z` admitted by `A_j`;
- frozen timing, off-target tolerances and discriminator class.

The covered domain is `C=union_j C_j`. The open-world remainder is defined, not discarded:

\[
U=T\setminus C.
\]

A finite family of cells need not reveal a complete mechanism. It must establish only the universal range and route/modulus fact needed for its declared cells. Hardware address ranges, type-safe state spaces, conservation/range invariants or independently proved monotone channel bounds can in principle discharge this narrower obligation. A sampled cloud, interpolation fit or statement that omitted states are unlikely does not.

For `z in C_j`, R169 gives

\[
e(z)\le E_{C,j}(z)
=\min\{M,E_B(v_j)+2R_j(z)\}
\le \min\{M,E_B(v_j)+2r_j\}.
\]

When cells overlap, take the minimum of every valid applicable cell envelope. This permits nested and overlapping actual processes and does not select one exclusive owner.

## 4. Sharp open-world envelope theorem

Assume only:

1. `0<=e(z)<=M` for all `z in T`;
2. `e(z)<=E_C(z)<=M` for all `z in C`;
3. no further constraint on `U=T\C`.

**Theorem R170-A (sharp pointwise remainder envelope).** Every compatible `e` satisfies `e<=overline E`, and `overline E` itself is compatible with exactly these premises. Therefore no smaller pointwise upper envelope follows without another premise.

**Proof.** The upper statement is the two-case definition. Compatibility follows by choosing `e=E_C` on `C` and `e=M` on `U`. This witness need not be a fully realized consumer-law family; it proves sharpness over the information class consisting only of the three declared premises. Any stronger physical sharpness claim would require a kernel-realizability theorem.

**Corollary R170-A1 (global-amplitude obstruction).** If `U` is nonempty, `sup_T e<=M` is the sharp general bound. If `U` is empty, `sup_T e<=sup_C E_C`. A measure-zero but nonempty remainder still blocks a nontrivial supremum claim.

This is the precise sense in which open-world honesty differs from a fictitious closed mechanism.

## 5. Sharp mean and exceedance bounds

Now additionally fix a target probability measure `mu` independently of the observed effects.

**Theorem R170-B (sharp mean remainder bound).**

\[
\int_T e\,d\mu
\le
\int_C E_C\,d\mu+M\mu(U).
\]

The information-class witness `e=overline E` attains equality. If `E_C<=b` and `mu(U)<=epsilon`, then

\[
\int_T e\,d\mu\le b+(M-b)\epsilon.
\]

This corollary is also sharp when the covered envelope is constantly `b` and the remainder has mass `epsilon`.

**Theorem R170-C (exceedance remainder bound).** For every `tau<M`,

\[
\{e>\tau\}\subseteq
\{z\in C:E_C(z)>\tau\}\cup U,
\]

so

\[
\mu\{e>\tau\}\le
\mu\{z\in C:E_C(z)>\tau\}+\mu(U).
\]

The sum can be capped at one. If `E_C<=tau` on `C` and `mu(U)<=epsilon`, the affected mass above `tau` is at most `epsilon`. This says nothing about the maximum effect inside `U`.

The measure and confidence events must be tracked explicitly. A statistical upper bound `mu(U)<=epsilon` can replace the true mass only on its own valid event; it cannot be combined with route bounds from a dependent split unless simultaneous validity is proved.

## 6. Why unknown mass is not unknown amplitude

For every `epsilon>0`, let `mu(U)=epsilon`, set `e=0` on `C`, and set `e=M` on `U`. Then the mean is `M epsilon`, the mass above any `tau<M` is `epsilon`, and the supremum is still `M`. Taking `epsilon` toward zero never lowers the supremum.

At `epsilon=0`, an almost-everywhere claim still does not imply a pointwise amplitude claim when a nonempty null set is physically admissible. Eliminating that set requires a target-domain exclusion, continuity/modulus bridge to covered points, or a separate amplitude certificate on it.

This exact countermodel prevents R168's random no-detection result from being promoted into route closure or maximum-effect control.

## 7. Coverage challenges and falsification

An open-world certificate should be challenged on its admission boundary rather than judged only on already admitted nodes.

Predeclare held-out actual contexts generated from the target specification but withheld from cell construction. For each challenge `z`:

1. the admission procedure must return a cell and anchor, or explicitly classify `z` into `U`;
2. a claimed cell route must meet identity, fidelity and budget clauses;
3. a valid consumer-law lower bound must not exceed the frozen cell/path upper budget;
4. the empirical frequency or structural mass of contexts classified into `U` must respect any claimed `epsilon` certificate under its declared sampling frame.

Failure of 1–3 refutes the cell/route coverage certificate. Failure of 4 refutes the mass remainder certificate. Neither failure is evidence for no mediator, no experience or false C1. Passing finite challenges does not prove an unbounded domain complete; it validates only the declared coverage method and confidence event.

## 8. Status logic

For one named target-domain certificate:

1. `INVALID_OPEN_WORLD_PROTOCOL` if target identity, admission, measure, timing, consumer geometry, safety or measurement validity fails.
2. `COVERAGE_CERTIFICATE_REFUTED` if a valid held-out context violates cell admission/route/budget or the claimed remainder-mass bound.
3. `CLOSED_DOMAIN_AMPLITUDE_CERTIFIED` only if every target context is structurally covered (`U` proven empty) and the R169/cell envelopes are valid.
4. `OPEN_WORLD_MASS_CERTIFIED` if a valid `mu(U)<=epsilon` certificate supports the mean/exceedance bounds while amplitude on `U` remains bounded only by `M`.
5. `UNRESOLVED` otherwise.

The two certified states are not ordered versions of one conclusion: one controls pointwise/global amplitude through closure, while the other controls only a measure-weighted target and preserves the amplitude obstruction.

## 9. Countermodels and failure modes

1. **Tiny rare branch.** An omitted actual branch has mass `10^-9` and effect `M`. Mean impact is tiny; global amplitude is maximal.
2. **Endpoint-only continuum.** Certified endpoints have zero effect while an interior gate has effect `M`. No within-cell route bound exists.
3. **Convenience measure.** A laboratory sampling measure assigns zero mass to a safety-critical admissible state. It cannot support a claim about the operational target measure.
4. **Post-hoc remainder.** Difficult challenges are relabeled outside `T` after observation. The target-domain contract is invalid.
5. **Overlapping cells.** Two valid cells overlap and give different upper envelopes. Their minimum is valid; overlap does not imply two competing exclusive subjects.

## 10. Preserved thought-experiment families

1. **Ancestor/formation.** A rare newly formed branch belongs to `U` until the admission specification covers it. Low evolutionary frequency does not deny its actuality or basal experience.
2. **Abacus/calculator.** A finite address decoder and verified carry range can provide a structural cell cover without reverse engineering the entire machine. An undocumented carry wire remains explicit remainder.
3. **Human-realized agent.** Safety-limited bodily/device configurations can receive a mass certificate while extreme untested configurations retain amplitude `M`. Nested human/device processes remain allowed.
4. **Copy/swap/memory.** A copied interface may share the observed measure while containing a new hidden admissible state. Target identity and coverage provenance must be re-established after the swap.

## 11. Direction, novelty and explanatory boundary

The decomposition, integration inequality, set inclusion and extremal witnesses are elementary established mathematics. No mathematical priority claim is made. The project-specific contribution is to attach them to R169's typed actual-route witness so that omitted contexts remain explicit and different scientific targets receive exactly the strength their premises support.

R170 supplies an evidence boundary for an organization-level route claim. It does not establish a target inventory, apparatus, neural mechanism, complete organization, C1, `B_min`, familiar bodily mineness, conceptual self or report truth. It does not add coverage, self-model, language, integration, recursion, prediction or control as a basal-experience requirement. It does not select a unique owner and does not determine whether the current assistant is conscious.

## 12. Next exact question

Which physically checkable target-domain specifications—finite hardware state ranges, typed program states, bounded sensorimotor manifolds or biological safety envelopes—can discharge the R170 admission/cell contract without circularly defining the target by observed success, and what minimal evidence distinguishes a real universal range proof from a fitted cover?
