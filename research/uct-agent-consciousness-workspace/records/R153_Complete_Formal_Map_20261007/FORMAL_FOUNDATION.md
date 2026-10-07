# R153 — Typed foundation, quantifiers and inference boundaries

7 October 2026. This is a research amendment to the existing map, not a change to any published edition. Goal: make every mapped object and inference inspectable and expose unsolved obligations. Scope: the 391 inherited node IDs and 188 inherited rule IDs, plus the integrated TA25 claim crosswalk. The node inventory is finite; its mathematical statements may quantify over arbitrarily large finite models, infinite sets, or actual physical occurrences. Inventory completeness is not a proof of semantic completeness.

## 1. What counts as a formal statement here

A contract has an object domain, fixed comparison parameters, a statement, premise routes, proof/evidence status, and exclusions. Statements use ordinary typed mathematics. They are **not proof-assistant terms**. Universal mathematical results require general proofs; checking a finite sample of models is only a counterexample/regression check. No parser or test below certifies the truth of unrestricted natural-language assertions.

For every rule, `all_of` is conjunction. Separate rules concluding the same node are alternatives. A theorem is a conditional statement over compatible instances of its premises, not permission to assert that all premise nodes are true in the real world. A source/evidence/context link is never a missing proof premise. Definitions and package construction do not turn their contents into established facts.

The formal use of a rule requires an instantiation certificate: the same object occurrences, times/horizons, signature, ports, target, probability law, policy class and epistemic interpretation wherever shared. Unifying words such as `self`, `state`, `organization` or `continuation` is not a certificate. The exported dependency routes are syntactic dependency expansions; substitutions are still mathematical obligations.

## 2. Ontology and interpretation: an explicit signature

Use a set-sized comparison universe (or an explicitly larger universe throughout). Let `Occ` be physical occurrences and let `Adm(P,I,b)` be the admitted-actual-token predicate at interval I and accountable boundary b. It requires the six source criteria: actual support, induced-relation fidelity, causal continuity, boundary accountability, lineage traceability and description invariance. **These criteria do not supply a complete physical decision procedure.** Their interpretation remains an ontology/application obligation.

For each admitted comparison fix a many-sorted signature K. It includes the constitutive carrier sort and every claimed operation, relation, pointing, time direction, constituent slot and port. For structures X,Y, `Iso_K(X,Y)` means a family of sortwise bijections preserving and reflecting every K relation and commuting with every K operation. Unnamed port permutations are not automatically admissible. Let `Type_K = Str_K / Iso_K` and `[X]_K` be a class. Structural completeness is relative to the actual token, not relative to whatever a convenient model happened to measure.

For admitted P write D_K(P) for its complete organization. **C1** asserts, for every such P, an experiential presentation Phi_K(P) and h_P with `Iso_K(D_K(P),Phi_K(P))`. The word experiential is an interpretive commitment; isomorphism alone does not define or independently verify that interpretation. There is no antecedent owner, report, correct self-model, recurrence, intelligence or exclusion threshold in this axiom. Admission and nonempty constitutive support are separate ontological premises.

Numerical equality P=Q, isomorphism D(P)≅D(Q), and causal lineage P↝Q have different types. Lineage can branch/merge. An actual macro token is not an arbitrary summary function. A finite model, its realization, and its containing implementation are three potentially different targets.

## 3. Experience, consciousness, capability and self

Use `E(P)` only as the proposition that Phi(P)'s distinguished constitutive carrier is nonempty. This basal existence predicate does not specify a scalar amount, valence, ownership or human-like content. Let k(omega)=[D(P_omega)] and e(omega)=[Phi(P_omega)] on the **same** configuration domain Omega and same actual bearer/time assignment. C1 identifies those structural classes. Merely assuming ker(k)=ker(e) is weaker than tokenwise C1.

Fix capability contract M: tasks, environments, resource limits, horizon, evaluated boundary, grounded ports, policy/adaptation class, score definition and distribution. Then J_M is a function on the realized complete-type image if the isomorphism invariance and omitted-context conditions hold. A score from one trial, a fitted estimate Jhat, and the exact distributional profile J_M are distinct. Ordering a vector requires an additional order/utility; unequal vectors are not necessarily ordered.

Keep six self-related targets distinct:

| Object | Type and precise role | Remaining interpretation |
|---|---|---|
| Actual bearer b(omega) | admitted occurrence parameter | Physical admission and boundary grounding |
| Actual target/attachment alpha | relation between bearer, target and ports | Whether the represented relation is constitutive |
| Internal attribution M_attr | installed system readout/disposition | Can be wrong; not the truth criterion for attachment |
| Predictive self model (m,d) | installed m:Omega→M and d:M×A0→Delta(Z), for fixed finite nonempty Z and common legal A0 | Accuracy does not establish installation, use or ownership |
| Conceptual Self_I | declared conceptual/autobiographical organization predicate | Exact semantic satisfaction criterion remains open |
| Felt mineness f_q | selected experiential target, formally q(e(omega)) only **if q is supplied** | No construction or empirical validation of q follows from writing this formula |

The worst-case predictive error is `sup_(omega,a) TV(d(m(omega),a),Q(omega,a))`. Wrong predictors remain members of the model class; their existence does not negate E. A conceptual-I absence witness is not automatically a witness of absent nonverbal mineness. Q can be the whole bearer, a proper constituent, a disjoint external target, or an overlapping target; these roles are relative to the specified bearer and do not form a forced exhaustive three-way partition.

## 4. Finite views and the three quantifier orders

With fixed v, D_v=Pi_v(D). An estimate Dhat_v is conditioned on evidence and model class. Neither equality of estimates nor equality of finite response laws implies complete-type equality. If a target f factors through representation r, there exists an abstract h on r(Omega) with f=h∘r. This existence statement contains no runtime, complexity, measurability, installation, access or causal-use guarantee.

The following are different:

1. `forall x, exists policy pi_x: succeeds(pi_x,x)` — individually solvable states.
2. `exists policy pi, forall x: succeeds(pi,x)` — one common implementable policy.
3. `forall task i, exists schedule si: completes(i,si)` — separate capabilities.
4. `exists schedule s, forall i: completes(i,s)` — simultaneous capability.

For two hidden states with good actions {0} and {1}, statement 1 holds and statement 2 fails. For n tasks sharing n−1 indivisible slots, every proper task subset is feasible and the whole set is not. Pairwise agreement/intersection is therefore insufficient for general joint consistency. The map must not exchange these quantifiers.

## 5. Proof spine, with all simultaneous premises

### P01 — C1, type equivalence and nonemptiness (a01–a03, a37)

Fix actual P,Q and common K. Given h_P:D(P)≅Phi(P), h_Q:D(Q)≅Phi(Q), any f:D(P)≅D(Q) gives h_Q f h_P^{-1}:Phi(P)≅Phi(Q). Conversely any g:Phi(P)≅Phi(Q) gives h_Q^{-1} g h_P. This proves the type biconditional. If D(P)'s distinguished carrier contains x, its image h_P(x) belongs to Phi(P)'s same carrier sort, proving nonemptiness. No inference about auxiliary empty sorts is needed. The universal axiom, physical admission and interpretation remain assumptions.

### P02 — Nonproduct whole (a14)

Fix actual W,P_1,…,P_n and a common product that transports constituent isomorphisms with the same slots/ports. Suppose D(W)≄product_i D(P_i). If Phi(W)≅product_i Phi(P_i), compose h_W, this alleged product isomorphism, and product_i h_i^{-1}; it would give D(W)≅product_i D(P_i), contradiction. Pairwise type biconditional alone cannot replace tokenwise C1 plus product compatibility. This proves nonproduct organization relative to that product, not unique subjecthood.

### P03 — Continuity and existence (a04, a19–a23)

Under C1, d(lambda)=[D(P_lambda)] and phi(lambda)=[Phi(P_lambda)] are the same map into the same predeclared quotient geometry. Hence continuity and all distances coincide, and an epsilon-chain transfers pointwise. This does not produce a continuous physical path. Independently, a continuous E:Lambda→{0,1}_discrete on connected nonempty Lambda is constant; E(lambda_h)=1 makes the constant one. Dropping continuity of E invalidates that route: on [-1,1], the physical coordinate lambda is continuous but E(lambda)=1 iff lambda>0 is not. E1 instead uses U1 on every admitted ancestor and needs no continuity premise.

### P04 — Set factorization and selected targets (c02, TA15:FIBER, R149)

For maps r:Omega→R and f:Omega→Y, a unique h:r(Omega)→Y with f=h∘r exists iff for all omega,omega', r(omega)=r(omega') implies f(omega)=f(omega'). Necessity is substitution. For sufficiency, assign to a realized r-value the common f-value of its nonempty fiber; this is well-defined and forced. There is no arbitrary representative choice of unequal values. Empty Omega causes no problem on the empty image. Claims of a total extension to R need their own nonempty codomain conditions.

Under the same-bearer C1 type biconditional, ker(e)=ker(k), so full e factors through r iff ker(r)⊆ker(k), equivalently k factors through r. If r=b∘k, this is equivalent to b injective on k(Omega). For a selected target f, only ker(r)⊆ker(f) is required. A constant f can be perfectly recovered despite loss of complete type. For J defined on complete types, different J entails different e; J identifies every e iff J is injective. Noninjectivity means **there exists** a nontrivial J-fiber, not that every fiber is nontrivial.

### P05 — Self-prediction radius (R146:SELF_TARGET_SUFFICIENCY)

With nonempty Omega, fixed nonempty finite Z and common legal plans A0, apply P04 to omega↦(Q(omega,a))_a. Abstract zero-error decoding exists iff every Q(.,a) is constant on each m-fiber. If two targets in one fiber have TV delta, triangle inequality forces at least one error ≥delta/2. The exact unrestricted optimum is `sup_(m,a) min_p sup_(omega:m(omega)=m) TV(p,Q(omega,a))`. On the finite simplex each inner objective is 1-Lipschitz and continuous; compactness gives a minimizer. Independent decoder rows can take their minimizers; a canonical lexicographic minimizer avoids ambiguity. This has no effective installation or measurability guarantee over arbitrary m,a. Three distinct point masses on three symbols have diameter one and radius 2/3, so half-diameter is not generally exact.

### P06 — Common quotient and stochastic joint law (a34, R126:P2, N128)

For onto p:S→Z and total deterministic F_a, a unique Fbar_a on Z with pF_a=Fbar_a p exists iff equal p-values imply equal next p-values, for every s,t,a. Define Fbar_a(z)=pF_a(s) at any s in p^{-1}(z); independence follows. If each p_i closes, (p_1,p_2) closes on its realized image by pairing the component updates. For Markov K_a the necessary/sufficient condition instead compares the **whole** pushed-forward row law p_*K_a(s,.). Equal marginal next laws do not suffice. At current (x,y,z), let next (X,Y)=(U,U XOR z): both marginals are fair but the joint laws for z=0,1 have disjoint support. Conditioning on persistent z=0 changes the domain and restores closure; it does not repair full-domain closure.

### P07 — Capability and time boundaries (R132, R136, R137)

For partial controlled kernels the preserved object is (enabled menu, joint next-summary/output law). Comparing common enabled rows alone omits menu differences. Matching separate state and output marginals omits dependence. The common decoder must have the same action distribution at every state in its visible fiber. A state-dependent decoder would exchange `exists decoder forall hidden states` with `forall hidden states exists decoder`.

If each conditional joint row has TV error ≤epsilon, same legal controller and fresh conditional randomization permit a stepwise maximal coupling while histories agree. Inductively agreement through H steps has probability at least (1−epsilon)^H; path TV is at most 1−(1−epsilon)^H≤min(1,H epsilon). The bound is for finite H. For fixed positive epsilon its limit is one, so no uniform small infinite-horizon error follows. Reusing one fair coin across H steps gives all correct one-time marginals but path TV `1−2^(1−H)` against H independent fair bits.

### P08 — Selection and transmission (c08–c11)

Let finite p, W≥0, barW>0. Selection gives psel_s=p_sW_s/barW. If W=f(J) and p(J=j)f(j)>0, divide by the corresponding class mass to obtain psel(s|j)=p(s|j). For copied trait C, mean change is Cov(W,C)/barW. For separately specified descendant trait mean Cprime_s, add and subtract sum p_sW_sC_s/barW to obtain Cov(W,C)/barW + E[W(Cprime−C)]/barW. Thus copying is required for the selection-only formula, not imposed simultaneously with nonzero transmission. For fixed K and strictly positive class weights, capability dynamics close for every p iff each row's destination-class sums are constant within current J classes: sufficiency groups sums; necessity compares two point-mass starts. Zero class weights would erase those starts and invalidate that necessity argument as stated.

### P09 — Decision value and information (c12, c20–c24, R127)

For fixed finite supported observation cells, common finite nonempty actions and payoff, a richer observation can ignore its extra coordinate. Fix a baseline-optimal action at each X=x. The value gain is the expectation of nonnegative conditional regret against the cellwise richer optimum; it is zero iff one baseline action is optimal in every supported richer cell at each x. Costly, destructive or late information changes this problem.

For same transcript laws P,Q and h∈[0,1], sum h(P−Q) is bounded in absolute value by the mass of the positive part of P−Q, namely TV. A common downstream kernel contracts TV. If two preparations at common supported (b,q) require different answers with errors epsilon_0,epsilon_1, their conditional cut TV is ≥max(0,1−epsilon_0−epsilon_1). Unfixed side information B must be included in the joint cut (C,B). C=X XOR B with independent fair B shows why marginal C alone fails.

Finite log loss is conditional entropy plus expected KL. Subtracting the Z and (Z,R) forms yields I(Y;R|Z)+K_Z−K_ZR. Adding Astar to mutual information and applying the chain rule gives I(Y;R|Z)≤H(Astar|Z)+I(Y;R|Astar,Z). The advertised fitted-gain bound also requires the independent K_Z≤eta premise.

### P10 — Symmetry and self-reference (a17–a18, R146, TA19)

For deterministic equivariant S, any automorphism g of W fixes the selected set as a set. If P is selected, all gP are selected, so the output is a union of orbits. A nonempty selection from one orbit must be that orbit; if it contains an overlapping pair it is not pairwise disjoint. For a singleton selector, its candidate must be fixed by the whole stabilizer. This does not obstruct the centered map iota(W,P)=P, which has a different input domain. It also does not install that map in a physical process or establish felt ownership.

For a covering pi:E→X, a continuous section composed with a based loop is a lift that returns to its own starting point. Unique lifting makes that point fixed by the loop's monodromy. No common fixed point therefore obstructs a global section. This is a necessary condition as stated; do not claim its converse without connectedness/covering hypotheses and a proof.

### P11 — Rewiring (R147)

Let controller and body sorts each have n≥2 elements, with bijections beta,sigma,tau and independently selectable command bits u. Substitute j=sigma(i) in x_j+=x_j XOR u_(tau^{-1}(j)) to get m_i+=m_i XOR u_(L(i)), L=tau^{-1}sigma. The installed predictor m_i XOR u_i is exact for every command iff L(i)=i: if unequal, a command separating those coordinates refutes it. Equal full response laws force equal L by those basis commands. Fixed L allows exactly n! choices of tau, with sigma=tau L.

Take beta=id. Ordinary sigma=tau=id and sigma=tau=g for a fixed-point-free permutation g have identical L=id but opposite predicates sigma(i)=tau(i)=beta(i). Renaming must transport beta as well; fixed-beta rewiring does not. Thus prediction accuracy does not identify attachment. To infer complete experiential type difference, separately assume actual realizations whose complete isomorphisms must preserve this beta-retaining relation, then apply P01. Nothing here selects a particular feeling or transfers a numerical subject.

### P12 — Bridge composition and nonfactorization (TA15, TA18, R149)

Relation composition requires the SAME actual intermediate z_T and jointly valid guards; two unrelated witnesses with the same displayed label do not compose. For metric maps, triangle inequality plus an L-Lipschitz second map gives epsilon_TU+L epsilon_ST. When error events have probabilities delta_1,delta_2, union bound gives coverage ≥max(0,1−delta_1−delta_2); independence is unnecessary, but incompatible experiments do not define the required common event space automatically.

AND and XNOR at (1,1) have the same actual and single-reset output values but differ at (0,0). If gamma retains that joint response and H only the shared trajectory, gamma cannot factor through H. An arbitrary Phi(gamma) **can** still factor through H, e.g. a constant Phi. Phenomenal nonfactorization needs explicit pair separation or actual complete-type difference plus C1. A target-preserving null equivalence is ker(Phi)-contained; complete-type preservation under C1 additionally requires containment in ker(k).

## 6. Joint consistency is context-indexed

The map contains rival hypotheses, countermodels, finite models with different operation sets, and historical conjectures. It is wrong to conjoin all node sentences as real-world facts. A comparison bundle must fix one context and then conjoin the chosen premise instances. For example, the following triple is inconsistent on a common pair:

`ker(e)=ker(k)`; `e=h∘r`; `r(x)=r(y) AND k(x)≠k(y)`.

Every pair of these constraints has a model. This supplies an explicit three-way consistency test that pairwise checks miss. By contrast U1, absence of a unique selector and an inaccurate self-model are compatible: a two-token symmetric structure with nonempty experiential presentations and an inaccurate installed predictor witnesses that limited compatibility. This is a relative model check, not proof of physical truth of C1 or consistency of every source interpretation.

## 7. Thought experiments as obligations

| Family | Fixed objects / variation | Formal role and limit |
|---|---|---|
| All ancestors and organization formation | Actual-token family, K and predeclared geometry; organization varies | Motivation plus conditional E1/E2/E3; graduality alone is not E3's binary-continuity premise |
| Abacus / calculator | Named device or person-device interaction, installed operations, time/resources | Definition test of actual bearer and installed competence; an observer's abstract decoding is insufficient |
| People implementing an intelligent agent | Participants, executed process and abstract algorithm distinguished; constituent persistence separately stated | Tests nested/whole capability and P02; no automatic sum or exclusive subject |
| Copies, rewiring and memory | beta versus sigma,tau; isolated records only in the stated special case | Counterexample to accuracy→attachment and memory equality→numerical identity; no direct report→felt-quality inference |

## 8. Unclosed obligations and completion criterion

The finite map is complete as an **enumerated contract and dependency ledger** only when every inherited node/rule is represented and every unresolved item is addressable. It is not thereby completely formalized in a proof assistant or globally semantically verified. `GAP_LEDGER.json` separates corrected map defects, preserved historical amendments, interpretation/physical obligations, exact numerical reproduction gaps and machine-proof gaps, with affected-node propagation. Source originals remain immutable. To close an obligation, supply the named proof, definition, realization evidence or source recovery and record a versioned discharge; changing its status label alone is insufficient.
