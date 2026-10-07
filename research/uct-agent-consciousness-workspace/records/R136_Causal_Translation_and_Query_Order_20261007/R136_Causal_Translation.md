# R136 — Universal decision comparison, causal translation and query order

7 October 2026, Asia/Shanghai. Parent: 44f730df32dc01c0556d1242e8140c17f3ac738b. Four pinned papers unchanged.

## 1. The question and the necessary correction

R135 compares capability guarantee regions. An existential matching policy for each profile does not itself exhibit a common physical translator. But a stronger universal decision comparison can imply a single translator in a precisely restricted model: this is the classical Blackwell theorem. It would be incorrect to strengthen R135's caution into a universal impossibility statement.

This round distinguishes three operations:

1. Comparing all decision problems after a fixed, one-shot experiment.
2. Simulating an exogenous observation stream using only information already available.
3. Choosing a resource-limited observation before learning which later task will be requested.

The results below provide an exact finite certificate for (2), and a sharp separation for (3). They do not solve arbitrary controlled feedback translation or identify actual complete organization. Blackwell comparison, causal transport and query-complexity methods are established mathematics; the contribution here is their explicit connection and scope in the four-paper map.

## 2. Static universal comparison really can supply a translator

Let Theta, X and Y be nonempty finite sets. A desired experiment P has rows P_theta(x); an available experiment Q has rows Q_theta(y). Fix a prior p with p_theta>0 for every theta. A stochastic translator R(x|y) is independent of theta. Observations are supplied before a single terminal decision, all finite randomized decision rules are available, and there are no costs, deadlines or intervention side effects omitted from the model.

For a finite action set A and real utility u(theta,a), let V_P(u) and V_Q(u) be the optimal prior-averaged utilities after observing P or Q.

**Theorem R136:BLACKWELL (classical finite randomization theorem).** The following are equivalent:

- There is one stochastic R such that P_theta(x)=sum_y Q_theta(y)R(x|y) for every theta,x.
- V_Q(u)>=V_P(u) for every finite action set and utility table.
- The same inequality holds for every utility table with the one action set A=X.

Utilities may equivalently be restricted to [0,1]; a global positive affine normalization preserves comparisons.

**Proof.** Given R, any decision rule after P can be run after Q by first sampling the translated observation. Its joint theta/action law is unchanged, proving the value comparison.

Conversely, S={QR:R row-stochastic} is a nonempty compact convex subset of the finite-dimensional space of theta-by-X matrices. If P is outside S, strict separation gives a real matrix c with

\[
\langle c,P\rangle>\max_R\langle c,QR\rangle.
\]

Take actions X and u(theta,x)=c(theta,x)/p_theta. Under P, the identity rule that reports the observed x achieves the left side, so V_P is at least that value. Every rule after Q is one row-stochastic R and achieves at most the right side. This contradicts the value comparison. Thus P belongs to S. The implication from all action sets to A=X is immediate. QED.

This is a mathematical randomized postprocessor, not an invertible organization isomorphism. Full support of p matters: a state with zero prior mass cannot be constrained by its Bayes values. The observation channels are fixed before varying utilities; the theorem does not let each task secretly choose a new sensor or move its observation deadline.

R135 varies weights over a fixed success-profile family. Here the utility table over hidden states and actions varies universally. These are different quantifiers, so the theorem does not contradict R135's profile/guarantee hierarchy.

## 3. A finite causal-stream certificate

Fix finite nonempty alphabets X_t,Y_t for t=1,...,H, H>=1, and a common finite hidden-parameter set Theta. Write X=product_t X_t and Y=product_t Y_t. Desired path laws P_theta on X and available path laws Q_theta on Y are exogenous: translator outputs and downstream actions do not alter the law of future Y. Theta is not observed.

A causal translator sees y_1,...,y_t when it must emit x_t, may retain memory and use private randomness independent of theta and the entire Y stream. It has no future observations or hidden-parameter access. It must use one implementation for all theta.

Let R(x|y) be a row-stochastic matrix on full paths. For every t<H, prefix x_<=t and pair y,y' with y_<=t=y'_<=t impose

\[
\sum_{x_{>t}}R(x_{\leq t},x_{>t}\mid y)
=\sum_{x_{>t}}R(x_{\leq t},x_{>t}\mid y').
\tag{C}
\]

These are linear nonanticipation constraints. Denote the resulting compact polytope by Causal(Y,X).

**Theorem R136:CAUSAL_LP.** A common causal translator reproduces all P_theta exactly iff the following finite linear system is feasible:

\[
R\geq0,\quad \sum_x R(x|y)=1,\quad (C),\qquad
P_\theta(x)=\sum_yQ_\theta(y)R(x|y)\quad\forall\theta,x.
\]

More generally define

\[
d_c(P\leftarrow Q)
=\min_{R\in\mathrm{Causal}(Y,X)}
\max_\theta\operatorname{TV}(P_\theta,Q_\theta R).
\]

Its minimum is attained, and it is a linear program: minimize z subject to the stochastic and causal constraints, e_theta,x>=P_theta(x)-(Q_theta R)(x), e_theta,x>=the negative of that quantity, and sum_x e_theta,x<=2z for every theta, with e,z nonnegative.

**Proof.** Any causal transducer generates an R whose output-prefix law depends only on the input prefix, hence (C). Its mixture against Q gives the stated path law because Y is exogenous and the private seed is independent.

For the reverse implication, let R_t(x_<=t|y_<=t) be the common prefix marginal defined by (C); R_0=1. At positive-probability prefixes set

\[
r_t(x_t|x_{<t},y_{\leq t})
=\frac{R_t(x_{\leq t}|y_{\leq t})}
{R_{t-1}(x_{<t}|y_{<t})}.
\]

Prefix consistency makes these stochastic rows. At zero denominators choose any row; the prefix is unreachable for that fixed input prefix, so the choice cannot change R. The product of the r_t telescopes to R. Independent private draws implement these rows, giving a common causal transducer. The absolute-value epigraph gives TV, and compactness of the causal polytope with continuity of the objective gives attainment. QED.

Constraints are imposed on the entire declared input alphabet, including unused strings; arbitrary causal extension on unused histories is permitted. The source law is matched for every theta, not merely after averaging over a prior. A separate translator for each theta is inadmissible.

This is an exogenous observation-stream result. For a controlled mechanism whose next observations respond to the translated actions, multiplying a fixed full-path law by R is generally invalid. One must formulate the joint interactive process and respect interventions; that extension remains open here.

## 4. Composition and preservation of downstream decisions

**Theorem R136:COMPOSITION.** For three compatible stream experiments P,Q,W with the same parameter set and clock,

\[
d_c(P\leftarrow W)
\leq d_c(P\leftarrow Q)+d_c(Q\leftarrow W).
\]

Every common downstream causal decision rule with [0,1] payoff g_theta(x,action_path), whose actions do not feed back into the stream and whose legal actions are unchanged, can be copied after a translator with a value loss of at most its worst-parameter TV error. The payoff uses the translated stream and decision path, not an additional correlation with the raw available stream Y; translator costs are excluded unless explicitly modeled.

**Proof.** Run a W-to-Q translator and a Q-to-P translator in sequence at each time using independent seeds. The composite is causal, so its full-path stochastic matrix is an admissible product SR. For each theta,

\[
\operatorname{TV}(P_\theta,W_\theta SR)
\leq\operatorname{TV}(P_\theta,Q_\theta R)
+\operatorname{TV}(Q_\theta R,W_\theta SR)
\leq\epsilon_1+\epsilon_2.
\]

The second inequality is contraction of TV under R. Minimize over attained optimizers. A copied downstream decision rule is another stochastic kernel on the stream and its action path; contraction and the [0,1] payoff bound give the second assertion. It is executable because the translator and decision rule are causal and their action menus are preserved. QED.

Zero distance thus means exact causal observation simulation in this finite model. Even simulation in both directions does not by itself provide a constituent-preserving, pointed physical isomorphism.

## 5. Deterministic prefix criterion

Suppose P_theta is concentrated on x(theta), and Q_theta on y(theta).

**Theorem R136:PREFIX.** Exact causal simulation exists iff for every theta,theta' and time t,

\[
y_{\leq t}(\theta)=y_{\leq t}(\theta')
\quad\Longrightarrow\quad
x_{\leq t}(\theta)=x_{\leq t}(\theta').
\]

If it exists, a deterministic translator suffices.

**Proof.** A common causal translator must have the same output-prefix distribution at the same observed prefix. It cannot be a point mass at two different desired prefixes. Conversely the condition defines a unique required x_t for each occurring y_<=t; output that value and extend arbitrarily to other histories. This rule is causal and correct for every theta. QED.

This applies C's fiber-constancy idea at every information deadline, not only to the completed record. The full-record condition at t=H alone is insufficient.

## 6. Complete records can match while timely simulation fails

Take Theta={0,1}, H=2, a blank symbol *, desired deterministic stream x(theta)=(theta,*), and available stream y(theta)=(*,theta).

**Theorem R136:DELAY_GAP.** An unrestricted offline translator reproduces the desired stream exactly, but

\[
d_c(P\leftarrow Q)=1/2.
\]

**Proof.** Offline, emit (y_2,*). Causally, the first input is always blank. Let p be the probability of first output 1. Under theta=0 the path-TV error is at least p; under theta=1 it is at least 1-p, since any wrong first symbol disagrees with the required point-mass path. The maximum is at least 1/2. Guess the first bit fairly and output blank second: each parameter has path-TV error exactly 1/2. QED.

Both completed records identify theta perfectly. An action that must use theta at the first deadline distinguishes them: desired success is one, available best worst-case success is one half. Waiting until the second step would change the task. This is not an error in static Blackwell comparison; its observation-before-decision protocol is not satisfied at the first deadline.

## 7. Task announced after resource commitment: a sharp family

Fix n>=2 and 0<=k<=n. A hidden bit string b in {0,1}^n is held fixed. During a preparation phase, a restricted reader may inspect at most k distinct coordinates. The choice of later reads may depend on earlier read values and private randomness, but not on a future query. The complete read transcript and private state may be retained; there is no separate memory-size constraint.

Only after preparation ends is a query q in {1,...,n} revealed. No further bit reads are possible. The output must guess b_q. Define the worst-case success value

\[
V_{n,k}=\sup_\pi\min_{b,q}\Pr_\pi[\widehat b_q=b_q].
\]

Nature selects b,q independently of the realized private seed. A full reader may retain all n coordinates. This is a query-access model, not an arbitrary k-bit compression of an already fully observed string, and not a quantum code.

**Theorem R136:QUERY_BOUND.**

\[
V_{n,k}=\frac12+\frac{k}{2n}.
\]

**Proof (upper bound).** Average over uniform independent b and q. Condition on the reader's private seed and completed adaptive read transcript. The transcript constrains the values of the inspected set S; every uninspected bit remains an independent fair bit. This follows because each adaptive choice was a function only of earlier inspected values and the seed. Since q was not available during preparation, uniform q lies in S with probability |S|/n. Even granting perfect answers when q is in S, average success is at most

\[
\frac{|S|}{n}+\frac12\left(1-\frac{|S|}{n}\right)
\leq\frac12+\frac{k}{2n}.
\]

Average over transcripts and seeds. Worst-case success cannot exceed this uniform average, which bounds every randomized adaptive policy.

**Proof (attainment).** Choose a uniformly random k-subset S, read it, answer exactly if q is in S, and otherwise use a fresh fair guess. For every fixed b,q the success is k/n+(1-k/n)/2. Hence its worst-case value matches the upper bound. QED.

For n=2,k=1 the value is exactly 3/4. Adaptivity cannot improve this bound. With k=n it is one, and with k=0 it is one half. Revealing q before preparation changes the protocol: one read then suffices for certainty.

## 8. Why separate task certificates do not compose here

**Corollary R136:TASK_ORDER.** For 1<=k<n, every fixed, pre-announced query task has the same full threshold-guarantee region for the restricted reader and full reader: the cube [0,1]^{2^n}. Nevertheless, when q is revealed only after preparation, their optimal robust successes are (1+k/n)/2 and one. In the common delayed-query evaluation coordinates (b,q), R135's directional guarantee loss from full reader to restricted reader is exactly

\[
\delta(C_{\rm full}\to C_{\rm restricted})=\frac{n-k}{2n};
\qquad \delta(C_{\rm restricted}\to C_{\rm full})=0.
\]

**Proof.** For a pre-announced q, reading b_q gives success one on every b, so every threshold vector in the cube is dominated on both systems. In the delayed-query protocol the full reader still has an all-one success profile, while QUERY_BOUND gives the restricted robust optimum.

Every attainable profile has entries at most one. Thus the maximal directed loss out of the full-reader set is achieved at its all-one vector; its distance to the restricted set is

\[
\min_{w\in C_{\rm restricted}}\max_{b,q}(1-w_{b,q})
=1-\max_w\min_{b,q}w_{b,q}=1-V_{n,k}.
\]

The full reader's all-one vector dominates every restricted profile, giving reverse zero loss. QED.

If an exact translator could reproduce the full reader's delayed-query response under the restricted reader's ports, time and read budget, attaching the source rule “answer the requested retained bit” would achieve success one, contradicting QUERY_BOUND. No such translator exists under that contract. This is a quantitative obstruction to the proposed translation, not a theorem that all task-equivalent systems lack a translator.

The order is crucial: for each q there exists a preparation tailored to q; there does not exist one pre-query preparation that supports certainty for every q. R135 required matching protocols already; this result demonstrates why the query-revelation schedule belongs in that protocol. It is not a counterexample to R135.

## 9. What this adds to the four-paper map

| Source | Present application | Boundary |
|---|---|---|
| A:C1 and complete pointed signature | Timing and operative relations matter to any claimed complete isomorphism | A finite simulator is not the complete actual structure |
| B §2/§2.1 and BAC | Translate outputs at their required times without consulting future observations; respect read/action ports and resources | No intervention transport follows from exogenous trace simulation |
| C §5.2/§5.3 | Prefix fiber constancy is the timed recovery condition; adding delayed-query capability can distinguish a profile that separate tasks leave unresolved | This is a finite functional distinction, not a new constitutive principle |
| D §4 | The joint consequences relevant to the actual decision must be retained, including the information-availability schedule | Final prediction accuracy is insufficient when action comes earlier |
| R133/R134 | One common policy must respect observable history and a persistent hidden state | Private randomness cannot be correlated with the hidden string or future query |
| R135 | Complete static decision comparison can be stronger than a fixed guarantee region; query-order gap has an exact directional loss | Do not interchange fixed task weighting, all utility tables and physical mechanism equivalence |

The existing R135:ACTUAL_PROFILE and R135:UCT_INTERPRETATION govern any experiential application. If a physically grounded timed capability separates complete actual types under a common signature, published C gives the corresponding conditional type distinction. Neither the numerical gaps 1/2 or 1/4 nor the read fraction k/n measures experiential amount. No report, memory or translation capacity is an experience-existence gate.

Historical connections: X04/X13/X31 concern transported encodings/ports; X07 concerns preserving time grain; X28 concerns matching present content but differing future response. The examples here are explanatory addenda, not proof of every historical scenario's physical premises. Verified archive: 38 named cases and 47 family rows, not a recovered thousands-item inventory.

## 10. Prior art and review scope

- Blackwell, Equivalent Comparisons of Experiments, Annals of Mathematical Statistics 24 (1953), 265–272, DOI 10.1214/aoms/1177729032. Publisher metadata was located but full text was blocked by its access page. The finite theorem is proved above; it is explicitly classical, not a new theorem credited to this project.
- Börgers, Notes on Blackwell Dominance, 3 December 2023, https://public.websites.umich.edu/~tborgers/BlackwellDominance.pdf. Read setup and Proposition 1 discussion/proof opening through PDF p.5. These are expository notes based on Blackwell/Girshick, not independent originality evidence.
- Backhoff, Beiglböck, Lin and Zalashko, Causal Transport in Discrete Time and Applications, SIAM Journal on Optimization 27(4), 2528–2562 (2017), DOI 10.1137/16M1080197. Author-hosted 2016 preprint https://www.mat.univie.ac.at/~mathias/Causal_arxive.pdf read through introduction, Definition 2.1 and Proposition 2.3. Causality as prefix-measurability/linear constraints is prior art. Our common-parameter, finite row-kernel certificate is a scoped application, not a claimed generalization in priority.
- Doriguello and Montanaro, Quantum Random Access Codes for Boolean Functions, Quantum 5, 402 (2021), https://arxiv.org/abs/2011.06535. Abstract checked for the established selective-retrieval problem and randomness distinctions. No quantum result is derived or used here. Our restriction is bit-query access before task revelation, not arbitrary short-message coding; the exact query bound is proved directly.
- The 2020 Markov-category comparison paper was located, but attempted HTML full text was unavailable. It is only a further literature lead. This is not an exhaustive prior-art search.

General statements were manually reviewed by the same assistant, not independently peer reviewed or formalized in a proof assistant. Exact finite checks accompany the proofs; no biological or learned-agent experiment was run.

## 11. Next theoretical obligation

Extend the causal-stream certificate to controlled feedback with declared operation translations: downstream interventions change later observations, so fixed exogenous path kernels no longer suffice. Seek a finite, mechanically checkable relation preserving pointed state, legal operations, timing and joint output transitions, and determine exactly which parts reduce to existing alternating/probabilistic simulation theory. Do not claim a new UCT-specific constitutive theorem or biological/AI correspondence from an abstract feasible certificate.

T2 OPEN; C3 intervention transport NOT_TESTED; valence OPEN. Theory first.
