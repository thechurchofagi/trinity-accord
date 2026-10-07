# R137 — Executable feedback interfaces and finite incompatibility witnesses

7 October 2026, Asia/Shanghai. Parent commit f7a85c373b34e5726482de26e927f87b629db520. Four pinned publication editions unchanged.

## 1. From passive stream translation to controlled dynamics

R136's path-kernel certificate assumes an exogenous observation stream. It cannot simply be reused when actions change future observations. R132 already gives exact closure for common native actions, and R135 bounds the error of copying policies under a common-action contract. The missing finite case addressed here is a declared action decoder: each requested abstract action is implemented by a distribution over concrete actions, using only the currently available observation.

The crucial order is:

\[
\exists\text{ one observable interface}\quad
\forall\text{ compatible hidden states}.
\]

A state-by-state choice with the quantifiers reversed may require inaccessible information. This issue is established in feedback-refinement and output-feedback control theory; it is not a newly discovered consciousness principle.

## 2. Finite model and implementable interface class

Let S,Z,O,A be finite nonempty sets, with alpha:S->Z onto. The observation z=alpha(s) is actually available before each action in this model; alpha is not merely an analyst's inaccessible state map. Concrete state s is Markov-sufficient, including persistent mechanism labels, physical memory, resources and clock where relevant. Let A(s) subset A be its legal concrete actions, and K(s,a;s',o) the joint successor/output kernel for legal actions.

The abstract controlled model has a nonempty legal request set U(z) and joint kernel

\[
\bar K(z,u;z',o),\qquad u\in U(z).
\]

Time, output meaning and initial pointed state correspond: z_0=alpha(s_0). Terminal stopping can be represented by declared absorbing states with legal terminal actions; it must not be invented to repair an empty menu.

For every concrete state/action define the projected joint row

\[
p_{s,a}(z',o)=\sum_{s':\alpha(s')=z'}K(s,a;s',o).
\]

For illegal actions its row can be filled arbitrarily because its weight will be forced to zero.

The interface class considered here is explicitly restricted to memoryless randomized action decoding:

\[
w_{z,u}\in\Delta(A),\qquad
a_t\sim w_{z_t,u_t}.
\]

It reads z and the current requested u, but not the hidden s, private model label, or any extra controller history. Draws use fresh randomness conditional on the entire preceding history, independent of the plant and controller randomness. Equivalently the conditional action law really is w_{z,u} at every invocation. A persistent shared seed is allowed only if it implements that same conditional law, or if its relevant memory is added to the declared model.

The abstract controller itself may be arbitrary and history-dependent, using the observed z/output/request history and its own independent randomness. Its policy is defined on every finite projected history ending at z and chooses only requests in U(z), including histories with zero probability under the nominal abstract model. This legal extension matters after an approximate mismatch; U(z) is nonempty but the extension must actually be specified. The interface's concrete action and private coins are not additional information supplied to that controller. Costs or resources omitted from the declared state/output/payoff are not automatically preserved.

This class is narrower than arbitrary history-dependent refinement, state-estimator interfaces, multi-step action implementations or full physical isomorphisms.

## 3. The simultaneous local certificate

For a fixed visible z and request u define F_z=alpha^{-1}(z), q=bar K(z,u), and for epsilon in [0,1]

\[
W_s^\epsilon=
\left\{w\in\Delta(A):
w_a=0\ (a\notin A(s)),\
\operatorname{TV}\!\left(\sum_a w_a p_{s,a},q\right)\leq\epsilon
\right\}.
\]

These are compact convex sets, possibly empty. Exact translation uses W_s^0.

**Theorem R137:LOCAL_LP.** A legal observable decoder for (z,u) with uniform row error at most epsilon exists iff

\[
\bigcap_{s\in F_z}W_s^\epsilon\ne\varnothing.
\]

This is a finite linear feasibility problem. Use one common vector w, its simplex and illegal-action zero constraints, and variables e_{s,r}>=0 for joint outcomes r=(z',o), with

\[
-e_{s,r}\leq\sum_a w_a p_{s,a}(r)-q(r)\leq e_{s,r},
\qquad \sum_r e_{s,r}\leq2\epsilon
\]

for every s. For epsilon=0 it is just common linear row matching. If the common legal action menu is nonempty, minimizing epsilon gives an attained value in [0,1]. If that menu is empty, the legal-interface problem is infeasible even at epsilon=1; probability approximation does not relax legality.

**Proof.** An implementable decoder has the same w for all hidden states sharing z. Legality is exactly its support condition, and the induced row is the displayed convex combination. Conversely any feasible w can be sampled from the available observation/request and yields precisely those legal rows. The absolute-value epigraph is the finite TV expression. Compactness gives attainment when there is any legal w. QED.

The statement is a necessary and sufficient certificate within the declared memoryless action-decoder class, for every represented start state. It is not a completeness theorem for every possible physical controller.

## 4. Exact closed-loop policy transport

Assume an exact feasible w_{z,u} has been selected for every z,u and is invoked with the conditional-randomness contract in §2.

**Theorem R137:CLOSED_LOOP.** From every concrete s_0 and paired abstract alpha(s_0), every abstract observable-history controller has exactly the same finite-horizon joint law of

\[
(z_0,u_0,o_1,z_1,u_1,o_2,z_2,\ldots)
\]

when run on the abstract model or through the concrete interface. The concrete execution is legal at every step. Thus every bounded payoff defined on this projected history is preserved.

Conversely, a fixed decoder from this class that preserves these laws for every start state and every abstract controller must satisfy the exact local row conditions.

**Proof.** Conditional on a concrete full history, the current s may be hidden but lies in F_z. The controller's next requested-action distribution depends only on the projected history and its private state. After fixing its request u, the decoder has law w_{z,u}; its mixture gives q at every s in F_z. Therefore conditioning on any distribution of hidden s still gives the same q. Induct on time, coupling the controller's private randomness or conditioning on its full seed. Legality follows from zero mass on actions illegal at any compatible s.

For necessity choose an arbitrary start s and a one-step controller requesting a specified u. Equality of the joint (next z,output) law forces sum_a w_{z,u,a}p_{s,a}=q. Legality forces the zero constraints. Vary s and u. QED.

This handles feedback: the controller may choose later requests from earlier outputs, and those requests may change subsequent states and observations. The argument works with conditional controlled rows, not one precomputed passive path distribution.

No distribution of concrete action labels, hidden states or omitted implementation costs is claimed to match the abstract description.

## 5. Approximate feedback transport

Now assume legal decoders exist for all z,u with row-TV error at most a uniform epsilon, and preserve the same conditional-randomness contract.

**Theorem R137:APPROX.** For every paired start and every abstract observable-history policy, the TV distance between its length-H projected closed-loop path laws is at most

\[
\beta_H=1-(1-\epsilon)^H\leq\min(1,H\epsilon).
\]

Consequently any common [0,1] payoff of that projected history changes by at most beta_H.

**Proof.** Share the abstract controller's random seed. While the projected histories agree, its requested u agrees. Conditional on any concrete history, the mixed joint row is within epsilon of q. A conditional mixture over hidden concrete histories retains this bound by convexity of TV. Maximally couple the next projected state/output; agreement survives each step with probability at least 1-epsilon. Lift the sampled concrete projected row to its concrete action/successor distribution using finite conditional probabilities. This preserves the correct concrete execution marginal. All H steps agree with probability at least (1-epsilon)^H, so the path laws differ by at most its complement. The payoff bound follows from TV. QED.

This reuses R135's classical coupling argument after replacing a native abstract action by an observation-compatible concrete mixture. Partial concrete menus are allowed because the decoder is legal at every visible fiber, even after a coupled mismatch. Controllers choose only requests in U(z), which is supplied as nonempty at each represented abstract state. No infinite-horizon small-error guarantee follows.

## 6. A finite witness for interface failure

Let m=|A|, the number of declared concrete action labels. Fix z,u and an error budget epsilon.

**Theorem R137:OBSTRUCTION.** If no common legal decoder reaches error epsilon, at most m concrete states in F_z already witness the failure:

\[
\bigcap_{s\in F_z}W_s^\epsilon=\varnothing
\quad\Longrightarrow\quad
\exists J\subseteq F_z,\ |J|\leq m,\
\bigcap_{s\in J}W_s^\epsilon=\varnothing.
\]

**Proof (finite Helly/Radon argument).** Work in the simplex's affine space of dimension m-1. Choose a minimal subfamily W_1,...,W_r with empty intersection. If r=1 there is nothing to prove. Otherwise minimality supplies w_i in every W_j except possibly W_i.

If r>m, these r points are affinely dependent. A nonzero coefficient vector with sum zero and weighted sum of points zero has nonempty positive and negative parts. Normalizing these parts gives one point w that belongs to both convex hulls. For each j, at least one of the two index groups omits j; all points w_i in that group belong to W_j. Convexity gives w in W_j. This contradicts empty intersection. Hence r<=m. QED.

The same proof works for an exact row target or any fixed positive error budget; TV constraints remain convex. This is a direct application of classical Helly geometry, not a new general geometric theorem. It limits the size of a local state obstruction for this fixed interface class. It does not bound the number of measured samples needed to discover a hidden state, nor certify a continuum from finitely sampled states.

## 7. Sharp obstructions and the hidden-state oracle

### 7.1 An obstruction requiring all m states

There are m>=2 hidden ready states i=1,...,m, all observed as ready, and m legal concrete actions a=1,...,m. Action a fails precisely in hidden state i=a and otherwise succeeds. Success and failure lead to distinct visible absorbing terminal states. The requested abstract action must succeed with probability one.

**Theorem R137:SHARP_OBSTRUCTION.** Every proper subset of hidden ready states has an exact common decoder, but all m do not. The minimum uniform row-TV error is 1/m and the optimal worst-case success is 1-1/m.

**Proof.** In state i, failure probability is w_i. Exactness requires w_i=0. Any proper subset omits an index j, so action j succeeds on that entire subset. All m constraints contradict sum_i w_i=1. For approximation, max_i w_i>=1/m, with equality for the uniform mixture. Since the desired next outcome is deterministic success, row-TV error equals the failure probability. QED.

For m=3, every pair of hidden states has a perfect translator; the three together do not. The best shared interface succeeds with probability 2/3. This is a higher-order compatibility obstruction, not a failure of any individual state's action availability. Its quantifier pattern is related to R132's common-realization warning, but the objects here are distributions over alternative action ports, not simultaneous resource-slot assignments.

### 7.2 Opposite hidden encodings

Two hidden ready states b=0,1 share one visible observation. Concrete actions a=0,1 are both legal, and succeed iff a=b. The abstract request asks for deterministic success.

**Theorem R137:OBSERVATION_GAP.** A decoder allowed to read b has zero error at each state. A decoder restricted to the visible ready label has minimum uniform row error 1/2. If the target is instead a fair success/failure coin, a common randomized decoder is exact, while neither deterministic action is exact.

**Proof.** Let w be the probability of action 0. The two success probabilities are w and 1-w. For the certain-success target, worst error is max(1-w,w), minimized at 1/2. For a fair target the required equations are w=1/2 and 1-w=1/2, uniquely solved by the equal mixture. Neither endpoint solves them. QED.

The blind opposite-action mechanism already appeared in R134; R137 uses it to audit a proposed decoder, not to claim a new original counterexample. Observing b through a separately justified, timely diagnostic changes the information contract and can restore deterministic exactness. No free diagnostic is assumed.

## 8. Randomness has a temporal implementation contract

Consider a one-state concrete system with actions 0,1 that output their action bit and return to the same state. The one-state abstract system has a single request whose output is a fresh fair bit at each step.

**Theorem R137:SEED_GAP.** Sampling the concrete action fairly and independently at every step is exact. Sampling one fair action once and reusing it for H>=1 steps preserves every one-time output marginal but gives path-TV error

\[
1-2^{1-H}.
\]

**Proof.** Fresh sampling gives all 2^H strings probability 2^{-H}, exactly as the abstract process. Reusing one coin puts probability 1/2 on each of the two constant strings. The total shared probability mass with the abstract law is 2 times 2^{-H}; TV is one minus this overlap. QED.

This does not refute CLOSED_LOOP: reused randomness violates its conditional action-law premise after the first output. A physical implementation with persistent hidden random memory must represent it; unconditional action marginals cannot silently replace the conditional decoder. This is the temporal counterpart of the joint-law discipline already present in D/R128/R132.

## 9. Connection, novelty and source-reading limits

| Existing anchor | R137 extension | Limit retained |
|---|---|---|
| B §2.1, pointed/port-aware translation | Same request must be realized with actually observable information and legal action ports | One-way randomized control refinement is not an invertible constitutive translation |
| C §5.2, fiber constancy | One common decoder distribution must work throughout the visible-state fiber | Nonempty per-state solution sets do not prove a common selection |
| D §4 and R132 joint closure | Match joint next visible state/output, and their conditional evolution in feedback | Matching one-time marginals is insufficient |
| R133 shared-policy discipline | No hidden-state oracle in the action decoder | Extra observations or stored history must be explicitly supplied |
| R135 policy error | Same finite-horizon coupling bound after lawful action decoding | Uniform represented-state premise, not a fitted average |
| R136 causal-stream limit | Conditional controlled kernels support adaptive feedback | Only the declared memoryless action-decoder class is characterized completely |

Under A:C1, experiential interpretation still requires actual valid process tokens and a common complete signature. The current finite view and action decoder do not establish those premises. R135:ACTUAL_PROFILE/R135:UCT_INTERPRETATION remain the applicable source bridge. A failed interface certificate does not mean the concrete system has no experience, and a successful one does not prove equal complete experiential type.

Prior art checked:

1. Reissig, Weber and Rungger, Feedback Refinement Relations for the Synthesis of Symbolic Controllers, IEEE Transactions on Automatic Control 62(4), 1781–1796 (2017), DOI 10.1109/TAC.2016.2593947, https://arxiv.org/abs/1503.03715. Read the preprint introduction and state-information discussion, Definition V.2, Theorem V.4 and controller-refinement statement VI.3 with associated proof passages. Observable information and admissible inputs are central prior art. Our finite stochastic row-equality/mixture certificate is not claimed to supersede their general set-valued theory.
2. Khaled, Zhang and Zamani, A Framework for Output-Feedback Symbolic Control, https://arxiv.org/abs/2011.14848, version 3 (2022). Abstract checked: directly relevant output-based controller refinement already exists. Full technical comparison not completed.
3. Nadali, Trivedi and Zamani, Stochastic Neural Simulation Relations for Control Transfer, PMLR 288, 597–620 (2025), https://proceedings.mlr.press/v288/nadali25a.html. Abstract checked: stochastic simulation-based transfer of controllers and behavioral guarantees is established recent work. No neural implementation or advantage over their method is claimed.
4. The obstruction proof is the classical finite Helly/Radon argument, given in full above. TV coupling, linear feasibility and mixtures are standard. No priority claim is made for them or for the reused opposite-action witness.

Pinned A C1/type-equivalence, B §2/§2.1, C §5.2/§5.3, D §4, R132 closure and R135–R136 limits were checked. Source bytes remain unchanged. Historical links are to X04/X13/X31 (ports/recoding), X07 (timing) and X28 (same content/different response); no new empirical realization is certified. Archive scope remains 38 named cases and 47 family rows.

## 10. Next theoretical target

The certificate assumes the visible alpha(s) is supplied and the decoder uses no additional history. Next distinguish failure of this restricted decoder from failure of every causal implementation: when can a finite, causally updated memory resolve the hidden-state conflict without an oracle or extra intervention? Specify its update from real observations, its resource/time cost and the compatibility of its state with the physical process. Study finite-memory refinement and its observation requirements before claiming general mechanism correspondence.

General proofs were reviewed by the same assistant, not independently peer reviewed or proof-assistant certified. No training or biological experiment. T2 OPEN; C3 intervention transport NOT_TESTED; valence OPEN.
