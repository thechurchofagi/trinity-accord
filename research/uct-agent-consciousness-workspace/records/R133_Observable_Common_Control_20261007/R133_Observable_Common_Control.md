# R133 — Observable common control under a persistent unknown mechanism

7 October 2026 (Asia/Shanghai). Parent research commit: `e381fa5a84ea7696447940319331be04b4f63a92`.

## 1. Question, provenance and claim status

R132 established a resource-compatible common witness and a complete finite partial interface. A remaining quantifier gap is

\[
\forall m\;\exists\pi_m\;\operatorname{Success}(m,\pi_m)
\quad\not\Rightarrow\quad
\exists\pi\in\Pi_{\rm obs}\;\forall m\;\operatorname{Success}(m,\pi).
\]

The right side demands one rule for acting on information actually available to its controller. Merely writing different optimal policies next to each other does not supply that rule. This round gives a finite-horizon certificate, an exact one-shot information requirement, and counterexamples about probing and persistent uncertainty.

These are conditional mathematical results. They are not measurements of experience, proof of C1, an additional U1 gate, a scalar richness measure, or biological/AI T2 closure. A, B, C and D retain their pinned editions. In particular, A:C1 is the internal constitutive axiom, not the identically numbered T2 obligation.

Lineage: C:P2_COORD supplies the fiber-factorization viewpoint; C:P7 already treats common optimal actions when additional information is freely available within a fixed decision problem. R131 distinguishes payoff identification from full-law identification. R132 supplies partial enabled menus, joint next-state/output laws, and the common-witness problem. The construction below specializes established partial-observation control methods. No claim of historical priority is made for support-state recursion, set covering, or nonrectangular uncertainty.

## 2. Typed finite model and information contract

Let M be a finite nonempty set of candidate mechanisms. Mechanism m has a finite nonempty sufficient state set S_m. Fix finite action and output alphabets U and O, with O nonempty. Write

\[
X=\bigsqcup_{m\in M}\{m\}\times S_m.
\]

The true m is selected once and stays fixed. Each state x=(m,s) has an enabled menu E_m(s) contained in U. For a in E_m(s), the joint transition/output kernel

\[
K_m(s,a;s',o)\geq0,\qquad \sum_{s',o}K_m(s,a;s',o)=1
\]

is specified. It never changes m. Resources, remaining opportunities and relevant clock variables must be represented in the state or in the finite horizon. Any scheduler and intervention semantics are fixed in this contract. An unmodeled action constraint invalidates physical application of the certificate.

The controller knows the family and a nonempty initial support B contained in X. It observes its own past actions and the emitted outputs. It does not directly observe m, s, E_m(s), or the target flag. If a real device exposes its menu, that observation must be explicitly included. No prior over m is assumed. A randomized policy is a distribution on actions conditional on the observable history; its randomization is independent of the hidden mechanism except through that history. Hidden-model-correlated advice is excluded.

For a nonempty support B define

\[
A(B)=\bigcap_{(m,s)\in B}E_m(s),
\qquad
B_{a,o}=\{(m,s'): \exists(m,s)\in B,\ K_m(s,a;s',o)>0\}.
\]

The policy must select a in A(B). Attempting an unavailable action is not a free test in this model; any such test needs its own defined transition and cost. Outputs with empty successor support are impossible and impose no continuation obligation.

Fix a target set G contained in X that is closed under every enabled action. For a reach-once objective, an explicit persistent success flag can supply this property. The controller may stop at any history. Stopping counts as success precisely on runs whose current state lies in G. We ask for success within at most H transitions, with probability one from every initial x in B. Early success cannot subsequently be lost; this condition is essential to the recursion below. At a non-goal dead end the task fails. Zero-step success means B is contained in G.

**Support invariant.** After any observable history that has positive probability from at least one initial x in B, the recursively updated support is exactly the set of current model/state pairs attainable along that history. Proof is induction: a pair is attainable on the next output iff it has a predecessor in the current support and a positive kernel entry for that output. The same m appears on both ends. Because the history is finite, the product of its positive transition factors is positive. Conditioning on a chosen action does not reveal an extra hidden-model label.

This support is a qualitative information state, not a posterior distribution or an actual complete organizational type. Its sufficiency below is objective-relative.

## 3. Finite-horizon common-control theorem

For all nonempty B define Boolean W_h(B) recursively:

\[
W_0(B)=[B\subseteq G],
\]

\[
W_{h+1}(B)=[B\subseteq G]\ \lor
\left[\exists a\in A(B)\;\forall o\in O:
B_{a,o}\ne\varnothing\Rightarrow W_h(B_{a,o})\right].
\]

**Theorem R133:COMMON_POLICY.** Under §2, W_H(B) is true iff there exists one observation-history policy that succeeds within H transitions with probability one from every x in B. A deterministic policy depending only on (B,h) suffices whenever any permitted randomized policy succeeds.

**Proof, deterministic case.** At H=0 the assertion is exactly the stopping condition. Assume the assertion for h. If B is contained in G, stop. Otherwise choose the action witnessing the second clause. It is executable from every possible current state. For each possible output, the induction hypothesis supplies one successful continuation from every state in that output's successor support. Branching on the actual observed output yields a single admissible policy. This proves sufficiency.

Conversely suppose a successful policy exists and B is not contained in G. It cannot stop successfully on every initial state. Its first action must be common-enabled. For every possible o, its continuation must succeed from every x' in B_{a,o}. If it failed with positive probability from one such x', a predecessor x in B and a positive transition to x' would make the whole policy fail with positive probability from x. This contradicts the assumed guarantee. The induction hypothesis then gives W_h(B_{a,o}) for every possible o, proving necessity.

**Randomized case.** At a history with B not contained in G, a winning randomized policy cannot put positive mass on stopping or an unavailable action. Choose any action of positive mass. If any reachable successor state had positive conditional failure probability under its continuation, multiplying by the positive action and transition probabilities gives positive failure probability from some predecessor. Thus every output branch of every positive-mass first action must itself admit a winning continuation. Induction purifies these continuations and then the first action. Finite action and output alphabets, and the fixed finite horizon, make the induction exhaustive. This establishes both the recurrence and the asserted deterministic representative. QED.

A constructive certificate consists of a chosen common action at each reached (B,h), the exact support update for each output, and goal-contained leaves. This is an AND/OR policy tree, not a list of model-specific plans. Its depth is at most H; the raw support domain has at most 2^|X|-1 elements. No efficient polynomial algorithm or minimal-memory controller is asserted.

**Boundaries.** The result concerns probability exactly one within a fixed finite horizon. It does not say support alone determines expected payoff, an optimal success probability below one, or arbitrary infinite-horizon objectives. One fair trial repeated until success succeeds eventually with probability one, while failure by any fixed H has probability 2^(-H)>0. Treating every infinite supported branch as an adversarial failure would give the wrong almost-sure conclusion. No extension to continuous-state or continuous-observation zero-measure events is made.

## 4. Exact one-shot information condition

Now specialize to a one-shot decision. Let M and U be finite and nonempty. For each m, let nonempty G_m contained in U be the actions that are enabled and successful with probability one. Suppose a cost-free deterministic observation h:M→Y arrives before the action, without changing these success sets. Only nonempty fibers matter.

**Theorem R133:CELL_ACTION.** There exists d:Y→U successful for every m iff

\[
\forall y\in h(M),\qquad\bigcap_{m:h(m)=y}G_m\ne\varnothing.
\]

**Proof.** A successful rule uses the same d(y) at every mechanism in a fiber, so this action lies in the intersection. Conversely choose an action from every nonempty intersection and define d(y) accordingly. A randomized rule succeeds with probability one only if its entire positive-mass support lies in the same intersection; it cannot remove an empty-intersection obstruction. QED.

This is a set-valued decision version of the fiber discipline in C:P2_COORD, with the successful-action interpretation related to C:P7. It does not require the successful action to identify m. Pairwise intersection is insufficient: G_1={a,b}, G_2={b,c}, G_3={a,c} have pairwise intersections but empty triple intersection.

**Theorem R133:MESSAGE_COVER.** Suppose the observation encoder h itself can be freely chosen, subject only to being a deterministic function of m, and there is no side information. Set C_a={m:a∈G_m}. The smallest number of used messages that enables guaranteed one-shot success equals

\[
\tau=\min\{|V|:V\subseteq U,\ \bigcup_{a\in V}C_a=M\}.
\]

Hence the minimum fixed-length binary message size is ceil(log_2 tau), with zero bits when tau=1.

**Proof.** For any successful encoder/decoder using k messages, each message cell is covered by the action selected for it. These at most k actions cover M, so tau≤k. Conversely take a minimum covering action set of size tau. Assign each m to one covering action and transmit its index; decoding to that action succeeds. Thus k≤tau. The binary statement follows from the number of available fixed-length words. QED.

This is an ideal task-information requirement, not a physical sensor construction. It assumes the encoder can access the required distinction, messages arrive before commitment, and sensing preserves the specified decision problem. It is neither entropy nor mutual information, does not address average code length or noisy channels, and is not a universal communication complexity theorem. If an allowed sensor family is fixed, the achievable message partition must also belong to that family.

## 5. Large model uncertainty with a small sufficient message

Let M=U={1,...,n}, n≥2, and let action a succeed iff a≠m. Every proper subset of mechanisms admits a common successful action, while the whole family does not: choose an action omitted from a proper subset; no action is omitted from all M.

**Theorem R133:AVOIDANCE.** In this family:

1. Every known mechanism has a successful action; no common deterministic unobserved action succeeds for all mechanisms.
2. The optimal randomized worst-case success without observation is 1-1/n.
3. Exactly two ideal messages suffice for guaranteed success for all mechanisms, even though complete model identification requires n different messages.

**Proof.** If action probabilities are p_a, success under m is 1-p_m. Thus the worst-case success is 1-max_m p_m≤1-1/n, with equality for the uniform distribution. One message cannot work by empty full intersection. Two suffice: report whether m=1; if yes use action 2, otherwise use action 1. Injective deterministic model identification requires n messages. QED.

For n=100 this gives a 99% optimal worst-case success without observation, no universally successful unobserved action, and a one-bit ideal diagnostic that yields 100% task success. These are exact features of this model, not a calibration statement about a real AI. Unlike R132's task-completion example, the quantifier here ranges over mutually exclusive mechanisms, not simultaneous tasks. Keep those interpretations separate.

No unique coarsest successful observation partition follows. With n=3 any pair of mechanisms can share a cell, but the all-three cell cannot. The three different two-cell partitions are each sufficient and mutually incomparable; a common coarsening of all three would be the failing one-cell partition. Thus a minimum message count need not identify one canonical partition. R132's unique coarsest exact stable refinement preserves a full specified interface; this task-relative criterion is weaker and has different uniqueness behavior.

## 6. Diagnosis must arrive while successful action remains possible

Consider two fixed mechanisms m∈{0,1}. Terminal action a_0 succeeds exactly for m=0 and a_1 exactly for m=1. Wrong terminal action enters an absorbing failed state. Both actions are initially enabled. Without a signal, deterministic worst-case success is zero; randomized optimum is 1/2. Each known mechanism individually has value one.

Specify three alternative probe interfaces, each with a one-transition probe p and terminal choices requiring another transition:

| Interface | Probe output | Post-probe state | Best worst-case success within H=2 |
|---|---|---|---|
| Preserving diagnostic | Exact m | Both terminal choices still available | 1 |
| Uninformative probe | Same symbol under both m | Same decision state | 1/2 |
| Destructive diagnostic | Exact m | Absorbing failed state | 1/2 if probe optional; 0 conditional on probing |

**Proposition R133:PROBE_BOUNDARY.** The displayed values follow from the specified model. The preserving diagnostic cannot give guaranteed success within H=1, but it does within H=2. Any finite number of uninformative no-effect probes does not raise the optimum above 1/2. Exact identification by the destructive probe is not sufficient for control.

**Proof.** After a preserving probe, output m selects a_m, so both mechanisms succeed. At H=1 no time remains to use its output; ignoring the probe and randomizing terminal choices attains 1/2 and cannot exceed it. With an uninformative probe, every policy's terminal-action distribution is identical under the two mechanisms. The two success probabilities sum to at most one (less if the policy never commits), so their minimum is at most 1/2. Uniform immediate commitment attains it. After a destructive probe no successful continuation exists, even though the support reveals the true model. If probing is optional, the same immediate randomized policy still attains 1/2, and allocating mass to the probe cannot improve the sum bound. QED.

All three cases are mathematical devices. No real-world destructive intervention is proposed. This does not refute C:P7's value-of-information statement: a free additional signal in a fixed action/payoff problem can be ignored, whereas the probe here consumes time and may change available actions and states. The certificate in §3 explicitly keeps those changes.

## 7. Do not replace a persistent model by per-step model switching

Take a forced two-stage protocol. Mechanism m=0 emits the pair (1,0); mechanism m=1 emits (0,1). There is no choice of action and the target is to have observed at least one 1 by stage two. Include phase and a persistent success flag in the state. The target set is closed.

**Proposition R133:PERSISTENCE.** The protocol succeeds under every fixed mechanism, but a stagewise uncertainty envelope that independently permits either mechanism's output at each phase contains the failing trace (0,0).

**Proof.** Both admissible complete traces contain a 1. Their possible first outputs and possible second outputs are both {0,1}; the Cartesian product of these marginal sets includes (0,0). This trace would require m=1 at the first stage and m=0 at the second. Such a switch violates the model contract. After first output 0, the correct support retains only m=1, whose second output is 1. QED.

This distinguishes a conservative envelope from the exact persistent-model problem. It does not imply every local envelope is strictly conservative, nor that Bayesian probabilities over models are necessary. The support invariant already retains the needed consistency. A model that really may change must encode the allowed switching process instead.

## 8. Relation to the four-paper map and thought experiments

| Foundation | R133 attachment | Limit |
|---|---|---|
| A: C1, U1, token/type distinctions | No change to experience-existence commitments; optional later interpretation must use actual complete organization | A controller's failed guarantee does not imply no experience; successful adaptation does not quantify richness |
| B: VIEW and admissible operations | The modeled observation, clock, menu, scheduler and resource boundaries must be specified | A mathematically available encoder or probe is not a grounded port |
| C: P2_COORD and P7 | Cellwise common actions; task information can be weaker than full identification; free signal distinguished from costly intervention | Complete-model identification is not generally necessary for the task |
| D: PAYOFF and joint consequences | Target-specific success sets and a single persistent process law | Marginal or retrospectively decoded facts do not supply an executable controller |
| R131: TARGET_SPAN / COMPLETE_LAW | Payoff, law, identity and action selection are different obligations | MESSAGE_COVER concerns actions, not full probability-law identification |
| R132: PARTIAL_MODEL / PARTIAL_CLOSURE | A persistent disjoint-union model plus observation support gives a common-policy certificate | Support sufficiency for bounded probability-one control is not full stochastic quotient closure |

Recovered cases X01 (different operating modes), X03 (measurement changes the mechanism), X05 (narrow readout), X08 (passive trajectory), and X09 (ongoing inputs) motivate parts of this analysis. Their historical descriptions are not automatically finite models satisfying §2. The mapping in CASE_CONNECTIONS.md distinguishes conceptual explanation from formal instantiation. The full several-thousand-item original inventory remains unverified; R131's 38 identified cases and 47 historical family rows retain their previous status.

## 9. Reading and originality audit

1. Chatterjee, Doyen and Henzinger, *Qualitative Analysis of Partially-observable Markov Decision Processes*, arXiv:0909.1645v3 (2010), https://arxiv.org/html/0909.1645v3. Read the observation-based strategy definitions in §2 and the subset-construction discussion in §3. These establish that qualitative partial-observation control and support constructions are prior art. Our bounded-horizon statement is proved directly; we do not present it as their infinite-horizon theorem or as a new classical discovery.
2. K. Takahashi, *Reusable Consequence States Under Partial Support and Model Uncertainty*, DOI 10.5281/zenodo.22170023 (2026-08-30), author abstract at https://kadubon.github.io/github.io/papers/2026-08-30-reusable-consequence-states-under-partial-support-and-model-uncertainty-22170023/. Abstract checked again; it explicitly discusses globally coupled candidate models and conservative local uncertainty envelopes. The linked full-text retrieval failed this round. No full-proof comparison or historical-priority clearance is claimed. This closely adjacent work must be examined before submission.
3. Pinned C §§5.2–5.3 and §7.3, pinned D/R96D target-relative decision discussion, and R132 §§5–9 provide the project source lineage. Published text and earlier proof nodes remain unchanged.

The incremental contribution within this project is the integrated information/action/time/persistence contract and its placement on the four-paper map, with explicit proof obligations and separating examples. A publishable original contribution still needs a sharper UCT-specific claim and a more complete literature comparison. A paper made only by renaming the standard control results would not justify a new foundational claim.

## 10. Next mathematical target

Replace perfect probability-one guarantees by a finite-horizon worst-case success level 1-epsilon under the same persistent model and permitted probe costs. Support alone then loses quantitative information: for example, two single-action experiments can have identical success/failure support but success probabilities 0.9 and 0.1. Do not take a separate minimum over mechanisms at each stage and call that the original objective. Start with model-indexed continuation payoff vectors or an equivalent nonrectangular formulation, retain one observable policy, and derive a justified information-versus-opportunity bound. Connect any resulting inequalities back to C:P7 and D:PAYOFF before considering experiments.

T2 remains OPEN; C3 intervention transport remains NOT_TESTED; the valence bridge remains OPEN. The present results are manually proved conditional mathematics with finite exact checks, not proof-assistant certification or independent physical validation.
