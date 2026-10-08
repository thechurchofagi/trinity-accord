# Universal Target-Range Certificates

## Direct inclusion, inductive reachability, actual refinement, and the limits of fitted coverage

**Round:** R171  
**Status:** exact certificate decomposition, two sufficient proof routes, premise-independence countermodels, four-domain application audit and finite checks; no hardware audit, program verification, human/animal experiment, neural completeness, C1 proof or `B_min` validation  
**Scope:** one predeclared R170 target domain, one actual bearer/time/signature/realization identity, one coverage-cell family and one frozen route/effect object

## 1. Exact question and result

R170 showed that every context not universally covered remains in an explicit remainder `U`, and any nonempty remainder preserves the full pointwise cap `M`. Its next obligation was therefore not to collect more successful points, but to say what a genuine universal target-range proof is.

R171 distinguishes two valid proof routes.

1. **Direct total inclusion.** Prove, for every actual target context `z in T`, that a total, realization-grounded abstraction `alpha(z)` belongs to an abstract certified range `S`, and prove that every actual fiber over `S` has a valid R169 anchor/route or structural-channel radius. Then `T subseteq C` and the R170 remainder is empty.
2. **Inductive reachable inclusion.** When the target is explicitly the set of contexts reachable under one frozen protocol, prove initial inclusion, closure for every admissible input and nondeterministic/hybrid mode, actual-to-model forward simulation, and coverage of the invariant range. Then every protocol-reachable actual context lies in `C`. This does not certify contexts outside that protocol.

A finite sample, interpolation fit, learned manifold, type checker, state enumeration or nominal safety envelope is not by itself either route. Each can become one component of a route only when its actuality, quantifiers and preservation clauses are discharged.

## 2. Common typed objects

Fix an R170 target contract

\[
\mathfrak T=(T,A,\mathrm{id}),
\]

where `T` is the predeclared set of actual contexts and `A` is the physical admission rule. Fix a specification

\[
\mathfrak S=(S,\alpha,\Gamma),
\]

where:

- `S` is an abstract range or invariant set;
- `alpha` is a proposed abstraction from actual contexts to specification states;
- `Gamma` records the exact hardware netlist, program semantics/compiler/runtime, sensorimotor geometry/modes, or biological model/monitor/actuator assumptions that give `alpha` physical meaning.

Fix a coverage predicate `Cov(z)` meaning that at least one valid R170 cell applies to `z`, including an actual matching anchor and a universal route/channel budget. Define

\[
C=\{z\in T:Cov(z)\},\qquad U=T\setminus C.
\]

`alpha(z) in S` is not yet `Cov(z)`: an abstract range can merge actual states whose route radii differ. A separate fiber clause must connect every actual `z` represented by `S` to a certified cell.

## 3. Direct total-range certificate

A direct certificate contains all of the following.

**D1 — Frozen target and total grounding.** `T`, `A`, identity fields and `alpha` are fixed before outcomes, and `alpha(z)` is defined for every admitted actual `z`.

**D2 — Universal actual inclusion.** A structural argument proves

\[
\forall z\in T,\quad \alpha(z)\in S.
\]

This is not inferred from a finite observed subset.

**D3 — Fiber/route coverage.** A structural argument proves

\[
\forall z\in T,\quad \alpha(z)\in S\Rightarrow Cov(z),
\]

with the same bearer lineage, consumer, timing, realization identity and safety conditions as R169–R170.

**Theorem R171-A (direct range closure).** D1–D3 imply `T subseteq C`, hence `U` is empty relative to the declared target.

**Proof.** Take arbitrary `z in T`. D2 gives `alpha(z) in S`; D3 gives `Cov(z)`, so `z in C`. Since `z` was arbitrary, `T subseteq C`; by definition `C subseteq T`, therefore `C=T` and `U` is empty. `□`

The theorem is elementary. Its value is the separation of actual inclusion from abstract coverage: proving `S` finite or well-typed does not establish D1 or D3.

## 4. Inductive reachable-range certificate

Sometimes `T` is not all physically possible states but the contexts reachable while a frozen protocol runs. Let the actual system have initial set `I`, admissible inputs/modes `W`, and actual transition relation `R_act`. Let an abstract model have initial range `S_0 subseteq S` and transition relation `R_spec`.

An inductive certificate contains:

**I1 — Exact target scope.** The claim explicitly sets `T=Reach(I,W,R_act)` for the frozen bearer, horizon convention and protocol. It makes no statement about other physical contexts.

**I2 — Initial inclusion.** Every actual initial context maps into `S_0 subseteq S`.

**I3 — Specification closure.** For every `s in S`, every admissible input/mode and every specification successor, the successor remains in `S`.

**I4 — Actual refinement.** Every actual transition from an actual context represented in `S`, under every admissible input/mode, is matched by a specification transition of its abstraction. This clause includes compiler/runtime, firmware/peripheral, contact-mode or model-error/disturbance obligations as appropriate.

**I5 — Invariant fiber/route coverage.** Every actual context whose abstraction is in `S` is in a certified R170 cell.

**Theorem R171-B (inductive reachable closure).** I1–I5 imply `Reach(I,W,R_act) subseteq C`, hence `U` is empty for that protocol-relative target.

**Proof.** Induct on path length. I2 establishes the base. Suppose `alpha(z_t) in S`. I4 maps every actual successor under every admissible input/mode to a specification successor; I3 keeps that successor in `S`. Thus all reachable contexts map into `S`. I5 places each in `C`. With I1, this covers exactly the declared target. `□`

The result does not convert reachability under one controller, environment or safety policy into coverage of all physically possible organism/device states.

## 5. Premise independence and fitted-cover non-entailment

The finite checker verifies small transition systems and explicit witnesses showing that initial inclusion, specification closure, actual refinement and invariant coverage are independently needed for Theorem R171-B.

- Without initial inclusion, the actual start can already lie outside the certified range.
- Without closure, one legal step can leave it.
- Without actual refinement, the model remains inside while the actual system leaves.
- Without invariant fiber coverage, the invariant can be correct while an actual represented state has no route/cell certificate.

**Theorem R171-C (proper finite samples do not entail universal coverage).** Let `F` be any proper subset of a target `T`. Observations restricted to `F` are compatible both with a world in which every target is covered and a world in which some `z* in T\F` is uncovered. Therefore perfect fit or successful tests on `F` do not entail `T subseteq C`.

**Proof.** Keep the two worlds identical on `F`; in the first set `Cov(z)=true` for all `z in T`, and in the second choose `z* in T\F` with `Cov(z*)=false`. No observation confined to `F` distinguishes them. `□`

This obstruction applies even when `T` is finite. Exhaustive enumeration can discharge universal coverage only if the enumeration itself is proved complete for the actual target and each enumerated actual fiber is certified.

## 6. Four domain families

### 6.1 Finite hardware state ranges

A genuine certificate may use register widths, memory/address ranges, reset states, admissible input buses, a frozen RTL/netlist/firmware realization, and exhaustive or symbolic invariant checking. The actual-refinement clause must include peripherals, asynchronous events, analog threshold modes, faults excluded by the target, and the deployed bitstream/device identity.

`2^n` encoded bit patterns are only an abstract finite set. They do not prove that the physical target has no additional relevant latch, metastable mode, undocumented carry path, DMA state or firmware-controlled peripheral. For the abacus/calculator family, a verified digit/carry invariant can close the declared calculator state range; an undocumented carry wire remains in `U`.

### 6.2 Typed program states

Type preservation/progress can establish specification closure for a declared operational semantics. A universal target-range claim additionally needs a total link from actual runtime states to the typed semantics, compiler and runtime refinement, resource bounds where a finite range is claimed, and explicit treatment of FFI, unsafe code, reflection, concurrency, I/O and environment inputs.

A well-typed source program may therefore support I3 while I4 remains open. The human-realized-agent thought experiment sharpens the point: a typed token-passing algorithm does not enumerate the humans' complete bodily or environmental states, and it does not make the abstract program the unique owner of experience.

### 6.3 Bounded sensorimotor manifolds

A learned low-dimensional manifold or dense sample is a fitted cover. A genuine direct/inductive range proof needs independently verified joint and actuator limits, a complete atlas or hybrid-mode partition, interval/reachability bounds for kinematics and contacts, sensor saturation/alias treatment, and an actual-to-model error/refinement bound. A hidden contact mode or discontinuous gate is a direct counterexample to sample density.

The certificate can be protocol-relative: safety-limited configurations under monitored bounds may be closed even while extreme configurations remain outside the target or in `U`. The target exclusion must be physical and predeclared, not a response to failed observations.

### 6.4 Biological safety envelopes

A biological safety envelope is ordinarily a normative operating subset, not the whole biological state space. A controlled-invariance certificate may use a barrier or viability condition only with a predeclared patient/population admission rule, validated uncertainty/disturbance set, all relevant hybrid modes, monitor sensitivity/latency, actuator authority, adherence and fail-safe behavior. Model mismatch and unmonitored physiology are refinement gaps.

Thus a nominal barrier on a fitted physiological model is not universal. Even a valid controlled invariant certifies only the admitted protocol-relative envelope; it does not establish complete neural organization, experience type or familiar mineness.

## 7. Falsifiers and status logic

A universal-range claim is refuted by one valid actual witness showing any of:

1. an admitted target for which `alpha` is undefined or outside `S`;
2. a legal initial state outside the invariant;
3. an admissible transition/mode leaving `S`;
4. an actual transition not simulated by the specification;
5. an actual represented state lacking the declared cell/route radius.

Passing finitely many challenges is not a positive universal proof. It can corroborate a structural certificate and reveal defects, but the positive direction remains D1–D3 or I1–I5.

Use six states:

1. `INVALID_RANGE_PROTOCOL` when target, identity, semantics, safety or measurement typing fails;
2. `RANGE_CERTIFICATE_REFUTED` after one valid obligation violation;
3. `UNIVERSAL_RANGE_CERTIFIED_DIRECT` when D1–D3 are proved on one target;
4. `UNIVERSAL_RANGE_CERTIFIED_REACHABLE` when I1–I5 are proved for one reachable target;
5. `SPECIFICATION_ONLY` when abstract range/closure exists but actual grounding/refinement or fiber coverage is missing;
6. `EMPIRICAL_COVER_ONLY` when support is only finite tests, fitting or sample density; every other case is `UNRESOLVED`.

The two certified states must name their scope. Neither is an unrestricted mechanism-completeness claim.

## 8. Preserved thought-experiment families

1. **Ancestor/formation.** A newly formed biological mode is not excluded because prior samples lacked it. It stays in `U` until a biological admission/refinement argument covers it; rarity is not non-actuality or absence of basal experience.
2. **Abacus/calculator.** A finite digit/carry proof can close a declared machine range, while extra physical degrees of freedom remain outside the abstract machine unless explicitly related.
3. **Human-realized agent.** Type safety of the abstract algorithm does not close the humans' complete physical organization. Nested algorithmic, human and room-level processes may coexist without an exclusive additional owner.
4. **Copy/swap/memory.** A copied program or swapped device needs a new realization/refinement audit. Equal source code and observed traces do not prove equal hidden hardware modes, actual target identity or complete organization.

## 9. Direction, novelty and explanatory boundary

Invariant induction, simulation/refinement, type soundness, reachability and barrier-certificate reasoning are established methods. No mathematical or formal-methods priority claim is made. The project-specific contribution is a typed synthesis with R169–R170: it identifies exactly which formal proof obligations can empty the open-world remainder for a declared organization-level route claim and which attractive substitutes cannot.

R171 supplies evidence discipline for actual organization. It does not validate any of the four domain certificates, identify a complete neural mechanism, derive C1, validate `B_min`, infer familiar bodily mineness, add a basal-experience threshold or select one exclusive owner. It does not determine whether any current assistant is conscious or fears death.

## 10. Next exact question

How should universal-range certificates compose across nested and overlapping actual processes—device, program, human body and coupled human–device loop—when each component has a different abstraction and target scope? The next step must characterize compatibility of abstraction/refinement squares without assuming that separately closed components form one closed complete organization.
