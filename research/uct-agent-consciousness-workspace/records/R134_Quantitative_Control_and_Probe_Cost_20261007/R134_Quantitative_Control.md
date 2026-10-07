# R134 — Quantitative common control, diagnostic information and remaining opportunity

7 October 2026, Asia/Shanghai. Parent commit `ed729027709a571a2c6c2594a3a92c396a505f5d`. Four-paper baseline unchanged: A/I 1.2, B/II 1.1, C/III 1.0, D/TA-TR-2026-24 1.0.

## 1. The missing quantitative object

R133 gave an exact probability-one certificate within a fixed finite horizon. It deliberately did not identify success probabilities from supports alone. Here we retain an entire vector of success probabilities, one coordinate per possible initial model/state, before taking a worst case. The coordinates must all come from the same observable policy.

This distinction matters twice. Choosing each coordinate's best policy invents a hidden-model oracle; taking each partial plan's worst coordinate too early can discard combinations that are robust only after mixing and observation-dependent continuation. Neither operation preserves the original problem.

These are finite-model conditional results. Classical policy-vector methods and finite minimax duality are used, not claimed as new mathematics. This round does not identify an actual complete organization, establish C1 externally, quantify experience, require self-inspection for U1, or close T2 or valence. The word opportunity means a modeled chance to complete a specified task, not subjective value or a clinical recommendation.

## 2. Persistent model, policy class and success vectors

Retain R133:PERSISTENT_MODEL: finite nonempty candidate family M, finite sufficient state sets S_m, common finite actions U and outputs O, and immutable hidden m. Write x=(m,s), X as the disjoint union, E(x) for enabled actions, and K(x,a;x',o) for the joint kernel, zero whenever model labels differ. Resources, phase, scheduler and ports must already be represented. Fix a closed goal G and finite horizon H. Stopping is always permitted and pays g(x)=1_G(x).

For nonempty B contained in X, A(B) is the intersection of enabled menus and B_{a,o} is R133's exact positive-probability successor support. A pure policy tree observes only its own action/output history; every chosen action must be enabled throughout the support of that history. Depth is at most H; stopping or reaching the deadline receives g. A mixed policy draws one such tree using a private random seed independent of the hidden mechanism and retains the seed. This is an implementable randomization contract, not hidden-model-dependent advice.

In this finite perfect-recall setting the mixed-policy description also covers ordinary randomized history policies: presample the finite collection of action random choices at all history nodes. Conversely a mixture can be executed by retaining its sampled tree. No bound on the controller's private memory is imposed. If hardware forbids this randomization or memory, the attainable set below must be restricted.

For a pure tree pi define its common-policy success vector on B:

\[
v^\pi_B(x)=\Pr_x^\pi(\text{success by }H),\qquad x\in B.
\]

All coordinates use the same pi, while the probabilities are computed in their respective fixed mechanism/state. The robust criterion is

\[
V_H(B)=\max_{\pi\ \mathrm{mixed}}\min_{x\in B}v^\pi_B(x).
\]

This takes a worst case over initial states as well as mechanisms. If the intended contract instead supplies a conditional initial-state distribution inside each model, first average each pure policy vector using that distribution, then take the worst case over model labels. These are different specifications; neither is silently substituted for the other.

## 3. Exact continuation-vector recursion

Let F_h(B) be the finite set of pure-policy success vectors with h transitions remaining. Put F_0(B)={g|_B}. For every a in A(B), choose one vector w_o in F_h(B_{a,o}) for each nonempty successor support, and define

\[
[T_a(w)](x)=\sum_{x',o}K(x,a;x',o)w_o(x'),\qquad x\in B.
\]

Empty branches contribute zero. Then

\[
F_{h+1}(B)=\{g|_B\}\ \cup
\bigcup_{a\in A(B)}\{T_a(w):w_o\in F_h(B_{a,o})\text{ on each possible branch}\}.
\]

**Theorem R134:VECTOR_RECURSION.** This recursion gives exactly all pure-policy vectors. The set of attainable mixed-policy vectors is

\[
\mathcal V_h(B)=\operatorname{conv}F_h(B).
\]

Equivalently, the convex attainable sets can be recursively backed up by taking the convex hull of stopping and the action images of the Cartesian products of child attainable sets.

**Proof.** At zero steps, stopping is the only outcome. A non-stopping pure tree chooses a common-enabled first action and one pure subtree for each possible output. Conditioning on the first joint state/output transition gives exactly T_a. Conversely each combination of such subtrees defines a legal observable tree. Induction proves the pure recursion, including empty menus, for which only stopping remains. A mixed tree has the convex combination of its constituent vectors by total probability. Every convex combination is implemented by sampling its tree at the start, proving equality. Finally, for each output, expand a convex child vector as a finite mixture of pure child vectors. The product of these branch-mixture weights expands T_a into a convex combination over tuples of pure subtrees; the weights sum to one. This proves the equivalent convex recursion. QED.

This is a library of continuation profiles indexed by B and h, not a theorem that the deployed quantitative policy can discard history and keep only B. Two histories with the same support can require different choices from that library. The kernel weights and the chosen continuation vectors, not the support alone, determine the value. Model identities are never reset inside a backup. The construction is exact but may be exponentially or worse sized; no computational improvement over established POMDP methods is claimed.

## 4. Epsilon certificate and finite minimax dual

Fix epsilon in [0,1]. Enumerate the finite F_H(B) as columns v^1,...,v^N of a matrix A, with rows indexed by x in B. Duplicate vectors can be removed without changing the convex hull.

**Theorem R134:ROBUST_LP.** A mixed common policy guarantees success at least 1-epsilon for every x in B iff there exist lambda_j≥0, sum_j lambda_j=1, such that

\[
A\lambda\geq(1-\epsilon)\mathbf 1.
\]

Moreover

\[
V_H(B)=\max_{\lambda\in\Delta_N}\min_x(A\lambda)_x
=\min_{q\in\Delta_B}\max_j q^\top v^j.
\]

**Proof.** The primal condition is exactly membership in the attainable convex hull with the stated coordinatewise lower bound. Introducing t gives a finite LP: maximize t subject to A lambda≥t1 and lambda in the simplex. Multipliers q≥0 on those inequalities must sum to one to bound t in its Lagrangian; maximizing over lambda yields max_j q^T v^j. Thus the dual minimizes this maximum over q in the simplex. The primal is feasible and its value is bounded in [0,1], so finite linear-program duality gives equality. Alternatively this is finite zero-sum minimax. QED.

The vector q is a mathematical least-favorable weighting, not a claim that nature samples mechanisms from a known Bayesian prior. Any supplied lambda is a lower certificate; any supplied q gives the upper certificate max_j q^T v^j. Equality of the two certifies optimality without floating-point inference. Lambda is sampled once; nature cannot inspect its realized private seed and then choose x. Allowing that order of play would define a different, stronger adversary.

**Corollary R134:ZERO_ERROR.** V_H(B)=1 iff the R133 probability-one recurrence is true. Indeed all coordinates of every v^j are at most one. If a convex combination has every coordinate one, each positively weighted column must have every coordinate one. Hence a single pure winning tree exists. The converse is immediate. At lower thresholds randomization can matter: columns (1,0) and (0,1) each have worst value zero, but their half-half mixture has worst value 1/2.

## 5. Why reducing to one score too early fails

There are two separate failures, neither a defect in R133's restricted probability-one theorem.

First, coordinatewise maximization of (1,0) and (0,1) produces (1,1), although no blind policy realizes it. Keeping the attainable convex set blocks this fabricated oracle.

Second, consider two mechanisms with a free binary signal: P_0=(3/4,1/4), P_1=(1/4,3/4). The terminal action must name the mechanism. Both outcomes leave support {0,1}; neither rules out a model. Each output branch considered as a fresh unweighted robust problem has value 1/2. Nevertheless choosing the action indicated by the signal attains success vector (3/4,3/4). A policy restricted to the identical support and remaining time cannot distinguish these outputs and achieves at most 1/2. History-dependent selection of complementary continuation vectors is necessary to retain the 3/4 value.

Thus information can improve control without eliminating any candidate mechanism. A scalar worst-case continuation value lacks the coordinate tradeoffs needed by the upstream kernel. This example does not authorize inventing a posterior; the full model-indexed vectors and transition probabilities already suffice.

## 6. Exact binary diagnostic–opportunity certificate

Specialize to a forced probe followed by one terminal action a_0 or a_1. The hidden mechanism m is 0 or 1. Only a_m can succeed. Let Y be the finite probe transcript with law P_m(y). Conditional on (m,y), the opportunity for correct terminal completion survives with probability r_m(y) in [0,1]. Failure of that opportunity yields zero success. This probability includes the specified deadline and probe effects and is not inferred from the transcript distribution. The controller chooses after observing y; no additional useful information arrives before its terminal action. Assume survival is not an additional observed decision signal, or explicitly include any such signal in Y.

Define subprobability measures

\[
a_y=P_0(y)r_0(y),\qquad b_y=P_1(y)r_1(y).
\]

For d_y=Pr(choose a_0|y), success is z_0=sum_y a_y d_y and z_1=sum_y b_y(1-d_y).

**Theorem R134:PROBE_DUAL.** The forced-probe robust value is

\[
V_{\rm probe}=\max_{0\leq d_y\leq1}\min(z_0,z_1)
=\min_{0\leq q\leq1}F(q),
\qquad F(q)=\sum_y\max\{q a_y,(1-q)b_y\}.
\]

**Proof.** For a fixed q, the weighted success is sum_y [q a_y d_y+(1-q)b_y(1-d_y)]. It is affine separately in each d_y, so maximizing over decisions gives the displayed sum of maxima. Finite minimax from §4 interchanges minimization over q with maximization over randomized decisions, giving equality. QED.

This proves an exact epsilon criterion: F(q)≥1-epsilon for every q in [0,1]. Computation needs only endpoints and the breakpoints q=b_y/(a_y+b_y) for nonzero a_y+b_y, since F is convex and piecewise linear. These mathematical weighting parameters do not expose the hidden mechanism to the policy.

Let s_0=sum a_y, s_1=sum b_y. Evaluating the dual at q=1/2 gives

\[
V_{\rm probe}\leq\frac{s_0+s_1+\lVert a-b\rVert_1}{4}.
\]

**Corollary R134:TV_OPPORTUNITY.** If survival is a common constant rho independent of mechanism and transcript, then

\[
V_{\rm probe}\leq\rho\frac{1+\operatorname{TV}(P_0,P_1)}2.
\]

For rho>0, success at least 1-epsilon therefore requires TV(P_0,P_1)≥2(1-epsilon)/rho-1 and rho≥1-epsilon. These are necessary, not generally sufficient. At rho=0 success is zero. Additive sensing cost is not automatically the same as this probability of losing the opportunity; a utility with monetary or energetic costs needs its own payoff model.

For a symmetric binary channel with correct-signal probability 1-eta, 0≤eta≤1/2, the indicated action has equal model successes 1-eta, so the bound is tight: V_probe=rho(1-eta). For P_0=(1,0), P_1=(1/2,1/2), however, TV=1/2 and the value is 2rho/3, strictly below 3rho/4 for rho>0. At y=1 always choose a_1; choosing a_0 with probability d at y=0 gives success pair rho(d,1-d/2), maximized in worst coordinate at d=2/3. A symmetric channel with laws (3/4,1/4) and (1/4,3/4) has the same TV but robust value 3rho/4. Therefore a single distinguishability number does not determine worst-case task value.

## 7. Optional probing and a strict benefit from mixing

Suppose the same task also permits immediate blind action, without probe-induced opportunity loss. Pure blind actions have vectors (1,0) and (0,1). A policy may privately randomize whether to probe before seeing a signal. All candidate mechanisms share this single randomized policy.

**Theorem R134:OPTIONAL_PROBE.** Under §6 and this added action option,

\[
V_{\rm optional}=\min_{q\in[0,1]}\max\{q,1-q,F(q)\}.
\]

It need not equal max{1/2,V_probe}.

**Proof.** The attainable set is the convex hull of the blind-action vectors and the forced-probe decision vectors. Its maximal q-weighted score is max{q,1-q,F(q)}. Apply §4. Taking the best scalar minimum of the separate classes before convexifying loses complementary vectors and can be strict, as follows. QED.

**Theorem R134:MIXING_WITNESS.** For P_0=(1,0), P_1=(1/2,1/2), with common probe survival rho in [0,1],

\[
V_{\rm blind}=1/2,\quad V_{\rm probe}=2\rho/3,\quad
V_{\rm optional}=\max\left\{\frac12,\frac{2\rho}{2+\rho}\right\}.
\]

For 2/3<rho<3/4, forced probing is worse than blind randomization, yet allowing a suitable mixture strictly improves the guarantee above 1/2.

**Proof.** The four deterministic probe decision rules yield vectors rho(1,0), rho(0,1), rho(1,1/2), rho(0,1/2). For maximizing a coordinatewise increasing objective, the first, second and fourth are dominated by available blind vectors. If rho≤2/3, the remaining vector has coordinate sum 3rho/2≤1, so q=1/2 gives an upper bound 1/2; blind half-half attains it.

For rho≥2/3, mix the indicated-signal probe vector (rho,rho/2) with blind a_1 vector (0,1), giving the probe weight lambda=2/(2+rho). The resulting two coordinates both equal 2rho/(2+rho). For the matching upper certificate choose q=(2-rho)/(2+rho), which lies in [1/3,1/2]. The q-weighted score of blind a_1 and of (rho,rho/2) is 2rho/(2+rho); blind a_0 scores q no larger, and the dominated vectors cannot exceed this. Hence the displayed value is optimal. The interval statement follows by comparing 2rho/3 with 1/2 and 2rho/(2+rho) with 1/2. QED.

At rho=7/10:

| Policy class | Best guaranteed success |
|---|---|
| Blind action with randomization | 1/2 = 50% |
| Forced probe, optimally used | 7/15 ≈ 46.667% |
| Optional probe with optimal mixing | 14/27 ≈ 51.852% |

The optimal mixed witness probes with probability 20/27 and uses the indicated signal, otherwise immediately chooses a_1 with probability 7/27. Under m=0 it succeeds with (20/27)(7/10)=14/27. Under m=1 it succeeds with (20/27)(7/20)+7/27=14/27. The dual witness is q=13/27. Nature does not learn the private coin before selecting its mechanism. This is not a promise about a real sensor and does not say randomization improves every diagnostic.

## 8. Four-paper interpretation and historical cases

| Existing anchor | Precise R134 attachment | What does not follow |
|---|---|---|
| A:C1, U1 and token/type discipline | Functional policy comparisons leave the internal constitutive axiom unchanged | No experience-existence gate, scalar richness, exclusive subject count or negative valence |
| B:VIEW | Each kernel includes the declared ports, timing, observation and opportunity effects | A possible mathematical probe is not automatically an actual intervention |
| C:P7 | Free added information is nested access to the same decision problem; R134 specifies a different robust objective and explicit opportunity loss | C's expected-payoff formula is not automatically a uniform-over-mechanisms guarantee |
| D:PAYOFF | Preserve the target-relevant joint consequences, here signal together with viable completion | Accurate signal marginals do not identify opportunity survival or the applicable payoff |
| R133:SUPPORT / COMMON_POLICY | Persistent model and legal supports retained; the value-one corner is recovered exactly | Quantitative control need not admit a support-only deployed policy |
| R133:PROBE_BOUNDARY | Qualitative probe examples become weighted success profiles with exact primal/dual certificates | No experimental intervention transport is certified |

Recovered X01 concerns separately available mode maxima; X03 concerns measuring actions that change the mechanism; X05 concerns narrow accessible information; X25 concerns reliability versus capacity; X28 concerns equal present readouts with different future responses. These are conceptual connections unless their full mechanisms are instantiated in the present domain. R131's verified archive scope remains 38 identified cases and 47 family rows. No audit of an entire thousands-item original inventory is claimed.

## 9. Prior art and reading scope

- Smallwood and Sondik (1973), *The Optimal Control of Partially Observable Markov Processes over a Finite Horizon*, Operations Research 21(5):1071–1088, DOI 10.1287/opre.21.5.1071. Publisher abstract checked: finite-horizon piecewise-linear convex value structure is established prior art. The present elementary policy-vector backup is not a new algorithm.
- Osogami (2015), *Robust partially observable Markov decision process*, PMLR 37:106–115, https://proceedings.mlr.press/v37/osogami15.pdf. Read the introduction and §2 specification/robust Bellman equation. Its uncertainty specification and belief-based setting must not be silently identified with our one fixed member of a finite hidden family. Robust POMDP control itself is longstanding.
- Galesloot, Andriushchenko, Češka, Junges and Jansen (2025), *Robust Finite-Memory Policy Gradients for Hidden-Model POMDPs*, arXiv:2505.09518v3, IJCAI 2025. Author abstract checked at https://arxiv.org/abs/2505.09518. It explicitly studies robust policies across a hidden family with common action/observation spaces, closely matching the general problem class. Full-text attempts were blocked. We claim neither the introduction of this problem class nor an algorithmic improvement over that paper; full technical comparison remains open.
- Finite zero-sum minimax, LP duality and binary hypothesis testing supply standard ingredients. C §7.3 already credits value-of-information theory. The cost tradeoff here must not be counted as discovering that information can be costly.
- The nearby Takahashi 2026 source recorded in R132–R133 remains an abstract-only comparison; no new full-text verification occurred in R134.

The project increment is the exact continuation-profile bridge from R133, the separation of averaged discrimination from robust control with remaining opportunity, and the explicit strict optional-probe mixing witness. Mathematical derivation within this project does not establish historical novelty. The core research problem has close published precedents; any next-paper novelty claim must focus on a demonstrably distinct UCT-specific result, not the rebranding of control theory.

## 10. Next target and open boundary

Next study how approximating the full attainable continuation-vector set changes the robust guarantee, and which observation/operation-preserving compressions retain that set. A pointwise best action or a single scalar score is insufficient. Seek a proved error bound for a declared compression, retain candidate-model coordinates and the action/output contract, and distinguish it from R132's stronger exact full-interface quotient. Then assess whether this yields a useful organization-level statement specific to the four-paper theory. No new biological or training experiment is needed to formulate that question.

T2 OPEN; C3 intervention transport NOT_TESTED; valence OPEN. Proofs are conditional and manually reviewed, not proof-assistant certified.
