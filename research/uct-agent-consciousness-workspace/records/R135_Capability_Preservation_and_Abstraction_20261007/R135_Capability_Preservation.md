# R135 — Capability guarantees, abstraction error and action legality

7 October 2026, Asia/Shanghai. Parent research commit: d4ce9b5a328048c86a79baa00d15bcb0a25709e6. Four-paper source editions unchanged.

## 1. The organization question being addressed

R134 retained the vector of outcomes of a single shared policy across candidate mechanisms. The next question is which part of this object a finite description must preserve to support a declared capability claim.

Three objects must be separated: the best value for one objective, the collection of simultaneously attainable success guarantees, and the full set of policy outcome profiles. None is automatically the complete actual organization in A:C1. B explicitly distinguishes finite views from complete organization; C:P2 supplies the injectivity/fiber criterion for identification. R135 makes the middle, task-relative level precise, gives a quantitative transfer certificate, and identifies a boundary where small model error is not enough.

The mathematical ingredients are convex minimax, support functions and coupling/simulation bounds. They have established prior art. These proofs are a project-level synthesis and boundary audit, not a claim to have discovered convex decision theory or approximate bisimulation.

## 2. Comparable capability profile sets

Fix n>=1 named evaluation coordinates. A coordinate may be an initial mechanism/state pair, as in R134, or a member of an explicitly fixed evaluation family. Coordinate meaning, task payoff, horizon, resources and observation protocol must agree between the two compared descriptions. The controller uses one common policy across these coordinates. It does not read the coordinate label unless that access is explicitly part of the protocol.

Let C and D be nonempty compact convex subsets of [0,1]^n. They represent attainable performance vectors under the two descriptions, including permitted private mixtures. In the finite-horizon R134 model they are convex hulls of finite pure-policy sets. Comparing them does not itself provide a physical policy translator.

Define their guarantee regions by

\[
\mathcal G(C)=\{b\in[0,1]^n:\exists v\in C,\ v\geq b\},
\]

with inequalities coordinatewise. A guarantee b asks for one policy whose success reaches every component of b simultaneously. It does not ask that the exact achieved vector equal b.

For q in the simplex Delta_n, define the nonnegative weighted optimum h_C(q)=max_{v in C} q dot v. Zero entries of q are allowed. Finally define the directed guarantee loss

\[
\delta(C\to D)=\max_{v\in C}\min_{w\in D}
\max_i(v_i-w_i)_+.
\]

Thus every capability profile available in C can be matched by some profile in D within delta downward loss in every coordinate. The selected w may depend on v, but it is one common vector across all coordinates; there is no separate target policy per coordinate. This existential property is weaker than a causal, executable transport of a named policy.

## 3. Exact certificate from weighted optima

**Theorem R135:DEFICIENCY.**

\[
\delta(C\to D)=
\max_{q\in\Delta_n}\bigl[h_C(q)-h_D(q)\bigr]_+.
\]

**Proof.** For fixed v, monotonicity of the positive-part operation and compactness imply

\[
\min_{w\in D}\max_i(v_i-w_i)_+
=\left[\min_{w\in D}\max_{q\in\Delta_n}q\cdot(v-w)\right]_+.
\]

The identity uses max_i z_i=max_{q in Delta_n} q dot z and max_i(z_i)_+=[max_i z_i]_+. Convex compact D and Delta_n, with a bilinear continuous payoff, permit finite-dimensional minimax:

\[
\left[\max_{q\in\Delta_n}\{q\cdot v-h_D(q)\}\right]_+.
\]

Maximize over v in C; the two maxima commute, and the inner maximum of q dot v is h_C(q). This yields the formula. The outer maxima and inner minima are attained by compactness. QED.

**Theorem R135:GUARANTEE_EQ.** The following are equivalent:

1. Every threshold guarantee of C is also attainable in D: G(C) is a subset of G(D).
2. delta(C->D)=0.
3. h_C(q)<=h_D(q) for every q in Delta_n.

Consequently G(C)=G(D) iff the weighted optima agree for all such q.

**Proof.** If every guarantee transfers, use b=v for each v in C; some w in D dominates it, giving zero loss. Conversely zero loss is attained and supplies such a dominating w for every v, hence for every b below v. The weighted criterion follows from DEFICIENCY. Apply both directions for equality. QED.

Convexity is essential to the all-weights criterion. If mixing is forbidden, C={(1/2,1/2)} and D={(1,0),(0,1)} satisfy h_C(q)<=h_D(q) for every nonnegative q but D cannot attain threshold (1/2,1/2). Convexifying D restores the missing policy. The theorem does not license randomization on hardware or in a protocol that excludes it.

## 4. Consequences and composition of errors

**Theorem R135:VALUE_BOUND.** If delta(C->D)<=epsilon, then:

- Every b in G(C) transfers to the clipped guarantee max(0,b-epsilon 1) in G(D).
- For any coordinatewise nondecreasing function F on [0,1]^n that is L-Lipschitz in the maximum norm,

\[
\sup_{v\in C}F(v)\leq\sup_{w\in D}F(w)+L\epsilon.
\]

- For a third nonempty compact convex set E,

\[
\delta(C\to E)\leq\delta(C\to D)+\delta(D\to E).
\]

**Proof.** Choose w in D with w>=v-epsilon 1; this proves the threshold claim. For the function claim put u=min(v,w) coordinatewise. Then u<=w and ||v-u||_infinity<=epsilon, so F(v)<=F(u)+L epsilon<=F(w)+L epsilon. Taking suprema gives the result. For composition, match each v to w in D with its first directed error, and w to z in E with the second. Then z>=v-(delta_CD+delta_DE)1. Take the maximum/minimum defining delta. QED.

In particular F(v)=min_i v_i is monotone and 1-Lipschitz. Therefore a two-sided guarantee distance at most epsilon bounds the difference in robust optimal success by epsilon. The same holds for every nonnegative normalized weighted optimum. This does not control a signed diagnostic objective that rewards deliberate failure in a coordinate, nor does it preserve the exact distribution of each named policy.

A zero directed distance is a task-relative preorder. Its symmetric zero classes identify equal guarantee regions, not necessarily equal attainable sets or equal organizations. The result concerns an entire declared family of threshold questions, not every possible future task.

## 5. Strict separation of what the summaries preserve

**Proposition R135:HIERARCHY.** The following finite examples separate the comparison levels.

First let

\[
C_1=\operatorname{conv}\{(0,0),(1,0),(0,1)\},\qquad
D_1=\operatorname{conv}\{(0,0),(1/2,1/2)\}.
\]

Both have optimal worst-coordinate success 1/2. Yet C_1 permits threshold (1,0), D_1 does not; delta(C_1->D_1)=1/2 and delta(D_1->C_1)=0. Equal robust scores do not identify the guarantee region.

Next let

\[
C_2=\operatorname{conv}\{(0,0),(1,1)\},\qquad
D_2=\operatorname{conv}\{(0,0),(1,1),(1,0)\}.
\]

Both guarantee regions are the entire square [0,1]^2, and all normalized nonnegative weighted optima equal one. Nevertheless D_2 can realize exact profile (1,0), while C_2 cannot. Thus even the complete family of positive weighted optimal values does not identify all policy behavior.

**Proof.** In the first example every C_1 vector has coordinate sum at most one; the diagonal point (1/2,1/2) is available in both. D_1 is contained in C_1, and every C_1 vector is dominated within 1/2 by (1/2,1/2); matching (1,0) requires error at least 1/2. In the second example (1,1) dominates every threshold in the square, but every C_2 vector has equal coordinates. These observations prove all assertions. QED.

These are finite policy-profile examples, not actual-brain realizations. Including the zero vector corresponds to an available always-failing stop choice; including (1,1) represents an always-successful choice. Changing which task is scored can expose distinctions hidden by the original guarantee region.

Preserving complete joint transition/output laws and legal action semantics can preserve all common observable policies. Preserving one task's guarantee region need not preserve those laws or named actions. The converse to full-interface preservation is therefore not supplied by these examples or by GUARANTEE_EQ.

## 6. A sufficient executable abstraction contract

Consider paired finite controlled models K_m on S_m and abstract models Kbar_m on Z_m for each persistent m. A map alpha_m:S_m->Z_m is fixed. Both sides use the same finite output alphabet O and the same finite action set U, with every action in U enabled in every represented state. Equivalently, U may be a fixed globally executable subset, but then every claim is relative to that subset, not to all physical controls.

Both controllers see only action/output histories and have the same private-randomness contract. Neither receives the hidden state or model label. Time steps, initial pointed states and action/output meanings agree. A terminal payoff g_m(s) in [0,1] is exactly preserved:

\[
g_m(s)=\bar g_m(\alpha_m(s)).
\]

Reach-once success fits by including a persistent success flag. A declared stop option can be encoded by absorbing stopped states and the same payoff on both sides. More general path-dependent tasks must first include their relevant memory in the state.

Assume uniformly over represented m,s,a:

\[
\operatorname{TV}\left((\alpha_m,\mathrm{id})_*K_m(s,a),
\bar K_m(\alpha_m(s),a)\right)\leq\epsilon,\qquad 0\leq\epsilon\leq1.
\]

This bound is on the **joint** next abstract state/output law, not separate marginals. It must hold at every state relevant to the claim, not only sampled or on-policy states. A finite data fit does not establish this uniform premise. The actual-to-abstract map, port meaning and physical adequacy are separately supplied assumptions, not inferred from the inequality.

## 7. Finite-horizon transport bound

**Theorem R135:POLICY_BOUND.** Under §6, running the same observable policy on both models from paired initial states gives, for every coordinate and horizon H,

\[
|v^\pi-\bar v^\pi|\leq\beta_H,\qquad
\beta_H=1-(1-\epsilon)^H\leq\min\{1,H\epsilon\}.
\]

**Proof.** Use the same private random seed. While output histories and the mapped states agree, the actions agree. Maximally couple the joint next mapped state/output laws; by the total-variation premise, their pair agrees with conditional probability at least 1-epsilon. For the concrete side, refine the sampled mapped state to a concrete successor using its conditional kernel distribution; finite states make this well-defined on positive-probability outcomes. This preserves both transition marginals.

Induction gives probability at least (1-epsilon)^H that all coupled steps agree. On that event the terminal payoffs agree. On its complement their difference in [0,1] is at most one. Taking expectation yields beta_H. The linear inequality is the elementary union/Bernoulli bound. The same coupling applies conditional on any sampled pure policy and hence to its mixture. Total common actions ensure the copied policy is legal even after a mismatch. QED.

The exact beta_H bound is sharp as a uniform terminal-success bound: a one-action model remains forever in a non-goal state, while the other moves to an absorbing goal with probability epsilon at each step. Their row TV error is epsilon, goals/payoffs correspond, and their success difference at H is exactly 1-(1-epsilon)^H.

This is a standard finite-horizon coupling/simulation argument. The exponent is not a new physical continuity law. It need not stay small at large horizons; fixed positive one-step error cannot certify indefinitely accurate control.

**Corollary R135:TRANSFER_BOUND.** Pull abstract success profiles back to the same initial-coordinate labels as the concrete profiles. Since the observable policy class is common and every copied policy has coordinate error at most beta_H, both directed guarantee losses are at most beta_H. In particular

\[
|V^*-\bar V^*|\leq\beta_H.
\]

If an abstract policy is eta-optimal for its robust objective, its copied concrete policy satisfies

\[
\min_i v^\pi_i\geq V^*-2\beta_H-\eta.
\]

Alternatively, a certified abstract policy guarantee b transfers directly to max(0,b-beta_H 1).

**Proof.** Copy each policy in either direction using the same labels and history rule; the policy bound gives both directed profile approximations. Apply VALUE_BOUND to minimum-coordinate success. For the selected policy combine its concrete/abstract loss beta_H, its eta suboptimality, and the optimal-value gap beta_H. QED.

The factor two concerns regret relative to the unknown concrete optimum; transferring a particular known guarantee uses only one beta_H. These are different statements. Exact zero-error matching recovers the compatible part of the earlier full-interface result; it still does not certify that the finite view is an actual complete type.

## 8. Why action legality cannot be omitted

Consider a partially observed, two-step system with states start, good, bad, goal. Goal is absorbing. Initial state is start. At start only p is enabled; at good only a is enabled and moves to goal; at bad no non-stop action is enabled. Stopping is always available but succeeds only at goal. Every transition emits the same symbol. Menus at corresponding states are identical between the models.

Model K_0 sends start under p to good with certainty. Model K_delta sends it to good with probability 1-delta and to bad with probability delta>0. All other defined kernel rows are identical. Their maximal joint row TV difference is delta under the identity state map, and their terminal goal predicates are identical.

**Proposition R135:LEGALITY_JUMP.** Under R133/R134's rule that an action must be enabled at every state compatible with the observed history, the two-step optimal success is one for K_0 but zero for K_delta, however small delta>0 is.

**Proof.** Under K_0, after p the only possible state is good, so a is legal and succeeds. Under K_delta, the identical output leaves both good and bad possible. The common enabled non-stop menu is empty. The controller must stop, which fails on both states; stopping initially also fails. Randomization cannot make an illegal action admissible. QED.

This is not a counterexample to POLICY_BOUND: its common total-action premise is violated. Pointwise agreement of state menus alone does not fix the problem, because small transition perturbations change the information support and hence the set of legal history policies.

If one instead defines attempting a at bad to be a legal action that fails, this is a different, totalized protocol. Then p followed by a attains 1-delta, and the discontinuity disappears in this example. A physical attempted operation cannot be assigned such semantics without justification.

The jump comes from an exact no-invalid-action constraint, not a sudden appearance or disappearance of experience. It is not a refutation of A's constitutive or continuity commitments. It shows that a derived capability coordinate with a support-based feasibility rule need not be continuous merely because transition probabilities vary continuously.

## 9. Conditional UCT interpretation

For actual valid process tokens, fix a common complete structural signature and an independently grounded evaluation family. Assume the map from complete type s to guarantee region G(s) is well-defined and invariant under the allowed structural isomorphisms. This requires the same tasks, ports, resources and observation rules; none follows from the finite examples alone.

**Corollary R135:UCT_INTERPRETATION.** Under those premises and A:C1:

- G(s) different from G(t) implies different complete types and hence different complete experiential types.
- G identifies complete experiential type on the declared actual domain iff s->G(s) is injective.
- A selected experiential/organizational coordinate is recoverable from G iff it is constant on G's fibers.

**Proof.** A well-defined function on complete types cannot take different values at the same type. C1 supplies the type-level experiential identification. The equality and coordinate clauses are precisely C:P2_FULL and C:P2_COORD applied to the newly specified capability map. QED.

This is an application of published C, not a new constitutive axiom. Equality of guarantee regions does not, by itself, establish injectivity. Conversely this paper does not prove that G must fail to be injective on every possible restricted actual domain. The finite hierarchy witnesses show losses between mathematical observation objects, not an empirically established pair of actual experiences.

The distinction is useful: a task-valid compression can be justified without claiming experiential equivalence. A task-invalid compression can be rejected without declaring the remaining process experience-free. No score, guarantee distance, beta_H or action-menu discontinuity is an experience amount or a new U1 gate.

## 10. Relation to four papers and recovered cases

| Anchor | R135 connection | Retained obligation |
|---|---|---|
| A:C1 and token/type discipline | Conditional interpretation only after actual support and a common complete signature are supplied | No complete ontology inferred from finite task success |
| B:VIEW and port-aware translation | Explicit state, time, action and joint output contract in §6 | Compression is not an invertible relabeling; actual ports require grounding |
| C:P1 / P2 | Guarantee-region capability map enters the published distinction and identification criteria | No new proof of C1 or a universal noninjectivity theorem |
| D:PAYOFF | The retained region is relative to fixed target consequences | Changing the task can reveal omitted distinctions |
| R132:PARTIAL_CLOSURE | Exact enabledness/joint-law discipline retained; approximate case exposes an extra support/legality issue | Small kernel error alone does not preserve the legal policy class |
| R134:VECTOR_RECURSION / ROBUST_LP | Full policy profiles induce a guarantee region and directional transfer error | No per-coordinate oracle or premature scalar collapse |

X04/X13 (recoding and rebuilt controls), X07 (time grain), X10 (rare coupling), X25 (reliability versus capacity), X28 (equal current readouts with different futures) and X31 (disturbance recoding) motivate the interface and horizon boundaries. These are current explanatory addenda, not new certifications of all their original physical premises. The verified historical scope remains 38 named cases and 47 family rows; the thousands-item original archive remains incompletely audited.

## 11. Prior art and source-reading limits

1. Diakonikolas and Yannakakis, Succinct Approximate Convex Pareto Curves, SODA 2008. Author abstract read at https://www.cs.columbia.edu/~ilias/papers/convex-pareto.html. It directly concerns compact convex performance representations and monotone linear optimization. Our additive directed guarantee error is proved here; no priority or superior compression algorithm is claimed. Full theorem-by-theorem comparison was not performed.
2. Bian and Abate, Bisimulation and Trace Equivalence in an Approximate Probabilistic Context, FoSSaCS 2017, pp. 321–337; extended version arXiv:1701.04547. Author/research abstract checked at https://research.google/pubs/bisimulation-and-trace-equivalence-in-an-approximate-probabilistic-context/. It establishes close prior art on finite-horizon trace-TV bounds and probabilistic property preservation. The coupling-to-task implication is not claimed as new.
3. Lobel and Parr, An Optimal Tightness Bound for the Simulation Lemma, Reinforcement Learning Journal 2 (2024), pp. 785–797. Primary PDF https://rlj.cs.umass.edu/2024/papers/RLJ_RLC_2024_106.pdf; read introduction and §3 through the overlap-based error discussion. This is close prior art for compounding transition-error bounds. Our finite-horizon bounded-terminal-payoff setting differs from its stated discounted-reward setting; this is a scope distinction, not evidence of originality.
4. Prior R133–R134 sources on partial observation, hidden models and robust control remain applicable. Their incomplete full-text comparisons remain incomplete. An additional Oxford multi-objective model-checking record was inaccessible this round and is not treated as reviewed evidence.
5. Pinned B §2/§2.1, C §2/§5.1–§5.3 and D §4 were used for the organization, identification and payoff boundaries. Published bytes were not edited.

Convex separation/minimax and coupling are standard. The project increment is the guarantee-versus-profile hierarchy, explicit directional error certificate, its connection to policy transport, and the action-legality discontinuity that limits approximation in the existing map. Mathematical review here is conditional and by the same assistant, not independent peer review or proof-assistant certification.

## 12. Next theoretical question

A guarantee-region comparison permits a different implementing policy for each requested profile. A full mechanism correspondence needs one declared, causal translator that respects action/observation history, composition and timing. Next ask when task-relative guarantee preservation admits such a reusable translator, and construct a separating example if it does not. This directly targets the gap between preserved task success and B's port-aware mechanism correspondence. Do not infer biological/AI T2 closure from the mathematical existence of that translator.

T2 OPEN; C3 intervention transport NOT_TESTED; valence OPEN. Theory first; no new experimental run.
