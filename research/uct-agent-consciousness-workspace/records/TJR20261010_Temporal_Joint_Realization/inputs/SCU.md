---
title: "Matched Behavior and Source Use"
subtitle: "Exact intervention protocols, consumer classes, and limits of sensorimotor interpretation"
author: "Hongju Liu"
date: "10 October 2026 · SCU-PAPER-v1.0.1"
lang: en
fontsize: 11pt
geometry: margin=25mm
colorlinks: true
linkcolor: NavyBlue
urlcolor: NavyBlue
toc: false
---

**Status.** Preprint, SCU-PAPER-v1.0.1. This paper combines previously recorded R204 and R205 results with SCU20261010. It is a scoped theoretical and computational methods study developed with internal AI-assisted review; it has not undergone external peer review. No human or neural data were collected. The completed UCT map remains UCT-MAP-v1.1.2. Publication of these conditional results does not promote the pending map candidate.

**DOI:** [10.5281/zenodo.23272690](https://doi.org/10.5281/zenodo.23272690)

# Abstract

Successful action, accurate prediction, and actual use of a particular signal are different properties. Their separation is familiar, but an operational account must specify which organizational relation an intervention can identify and which alternatives remain indistinguishable. We give a finite, reproducible analysis of two consumers: an actuator and a pre-consequence predictor. Independently addressable source carriers have identical values in nominal trials, so different allocations of their consumers produce identical successful behavior and prediction. With fixed pure single-source consumers, a binary intervention code identifies whether the two consumers depend on the same root precisely when its source codewords are distinct. The resulting worst-case requirement is $\lceil\log_2 n\rceil$ probes for an unknown pair of roots, including deterministic adaptive protocols that observe only agreement or disagreement; one probe suffices when one root is independently known. These are applications of classical separation principles. Allowing both consumers independently to aggregate arbitrary nonempty sets of sources by OR changes the exact worst-case requirement to $n$. A four-source construction shows how a protocol valid for pure routes falsely accepts disjoint redundant source sets. Further countermodels separate root dependence from internal branch consumption, common ancestry from intake-occurrence identity, and prediction-state updates from comparator implementation. Exhaustive finite searches and event-model executions accompany the proofs. Under the inherited UCT correspondence axiom, actual constitutive source relations have experiential counterparts, but these results identify neither a particular feeling of agency or ownership nor a new threshold for basic experience. The contribution is a precise combination of target, mechanism class, probe cost, and interpretation boundary suitable for reuse in sensorimotor research.

**Keywords:** sensorimotor organization; causal intervention; source identification; separating systems; comparator models; agency; UCT.

# 1. The question and the contribution

Consider three installations that complete the same task and correctly predict the same sensory consequence. In one, an internal command drives the actuator and supplies the prediction. In another, an external apparatus drives the actuator while a synchronized internal signal supplies the prediction. In a third, a remote controller supplies both branches. Equal observed behavior does not tell us which installation is present. Calling the first signal “mine” or calling the last movement “passive” supplies no missing evidence about the implemented paths.

The question is therefore specific: **given a physically specified family of source carriers and a fixed pair of consumers, which interventions identify their source relation, under which mechanism assumptions, and with what remaining ambiguity?** A useful answer must distinguish a theorem about a finite model from evidence that an actual installation satisfies its premises. It must also distinguish a source relation from the experience that a person might describe using words such as agency, ownership, familiarity, or self.

The broad inadequacy of matching alone is established prior work. Zaadnoordijk, Besold, and Hunnius analyze why a match relation does not by itself explain the causal self-attribution needed in an account of a sense of agency [5]. Within the UCT program, TA25 already separates accurate prediction from physical attachment, including synchronized commands that hide a routing change [4]. Earlier modules distinguish actual consumers, shared carriers, equal-valued copies, and intervention-sensitive ports [10,14]. We inherit these distinctions. The published Task-Relative Continuity paper also derives a minimum route-tag alphabet for a supplied tag and a task-specific reader [13]. The present problem concerns actively chosen source interventions and a two-consumer disagreement readout, rather than that already established tag-reading problem.

This paper combines three narrower results. R204 supplies an exact separation of task success, prediction alignment, and feedback writing, including a reflex implementation that duplicates a comparator's prediction-state trajectories [11]. Concurrent R205 supplies a source-location/correspondence square and a cancellation construction in which whole-source interventions miss internally consumed branches [12]. SCU20261010 adds a comparison of identification protocols across two explicitly different consumer classes, a known-root shortcut, and an executable account of the boundary between source dependence and intake occurrences.

The paper does not claim a new general coding theorem. Pair separation and binary source labels are classical [6,7]; OR aggregation has established connections to superimposed codes and group testing [8]. Nor is perturbing predicted sensation to obtain diagnostic information a new research strategy: Ganesh and colleagues used prediction-error responses in an intention-decoding methodology [9]. The proposed knowledge increment is the exact assembly of a sensorimotor target, restricted readout, optimal probe requirements, mechanism-class counterexamples, and UCT interpretation contract. It is a methods synthesis and application, with independently executable negative controls.

# 2. Three levels of claim

## 2.1 Organization, experience, and evidence

We use the inherited UCT axiom C1 and its no-gate consequence U1 [1]. For an admitted actual process token $P$, C1 asserts a token-relative structural correspondence between its complete physical organization $\mathbf D(P)$ and its experiential organization $\Phi(P)$. At the level of complete structural types, it entails the corresponding equivalence. U1 does not make basal experience conditional on predictive accuracy, intelligence, memory, report, self-modeling, autonomy, or the source relations studied here.

These are interpretive commitments of UCT, not conclusions of the finite simulations. A mathematical source graph is a model. Its successful execution does not, by itself, establish the complete organization of a particular biological bearer. Executing a program also involves actual physical processes; this paper does not deny their UCT status. It does not identify those processes with every token described by the program or establish a selected phenomenal property of them.

Three levels will remain separate:

1. **Organizational result:** a theorem, construction, or counterexample in a declared model class.
2. **Conditional UCT interpretation:** what C1 implies if the specified relation belongs to the complete constitutive organization of an admitted actual token.
3. **Actual evidence:** observations and interventions that establish the required installation, boundary, chronology, and measurement premises in a particular system.

There is no human or neural dataset in this study. The third level remains an application obligation.

## 2.2 Five targets that must not be collapsed

In this paper, *task success* is a selected input-output criterion. It is not a complete measure of intelligence. UCT III treats capability profiles relative to fixed interfaces and distinguishes them from complete experiential type [3]. Equal success on the present task is consequently weaker than equality of capabilities, and either is weaker than complete organizational identity.

*Self-related organization* denotes specified relations within an admitted process: for example, a command's source, its consumer, or its connection to a bearer. *Conceptual self* concerns explicit representations or classifications of self; no such representation is required by the toy models. *Report* is an output action and is not interchangeable with either the organization or the experience reported. Finally, $H$ will denote a separately specified familiar self-related phenomenal target. The symbol is a placeholder for an independently anchored target, not an unmeasured label assigned to our simulated installations.

Agency, ownership, tactile intensity, discrimination sensitivity, and verbal endorsement can be relevant endpoints of different experiments. This paper does not identify them with one another. An actual study must specify which endpoint it measures and why its interpretation is justified. Requiring that evidence is not a new requirement for basal experience; it is a requirement for a particular explanatory or measurement claim [2,4].

## 2.3 Same-installation binding

Every identification claim fixes one installation contract

$$
\theta=(\mathcal W,B,\mathcal S,A,P,\kappa,\mathcal I,\mathcal O,\tau).
$$

Here $\mathcal W$ is the installation, $B$ the declared bearer candidate when relevant, $\mathcal S$ the physically named source ports, $A$ and $P$ the actuator and predictor consumers (the latter $P$ is a local consumer label, distinct from the process-token notation in §2.1), $\kappa$ the preparation/reset contract, $\mathcal I$ the allowed interventions, $\mathcal O$ the readout, and $\tau$ the temporal order. Each trial has its own interval and occurrences. The route parameters must remain fixed across the trials used in a single inference. A baseline from one installation cannot be combined with a probe from another merely because their outputs agree.

Resetting a trial supplies a preparation assumption. It does not prove numerical continuity with an earlier token or show what a consumer actually read in a past episode. When actual identity or retention matters, it must be established through the relevant physical relation and temporal evidence rather than inferred from a successful reset.

# 3. Success, alignment, and feedback use

This section presents the R204 results needed for the combined protocol [11]. Their provenance remains R204; reproducing them here is not a claim of a second discovery.

## 3.1 A finite separation

Let the action and consequence alphabets have the same finite size $m\geq2$. A plant $G$ maps actions to consequences, a forward predictor $F$ maps actions to predicted consequences, and a controller $C$ maps target consequences to actions. In the initial construction these maps are permutations. Define

$$
S=\mathbf1[G\circ C=\mathrm{id}],\qquad
K=\mathbf1[F=G].
$$

Let $U\in\{0,1\}$ be an independently installed feedback-writing gate. For a feedback event at action $a$ with delivered value $z$, the selected predictor row is updated by

$$
F^+(x)=
\begin{cases}
z,&U=1\text{ and }x=a,\\
F(x),&\text{otherwise}.
\end{cases}
$$

After an update $F^+$ need only be a total function; it need not remain a permutation.

**Proposition 1 (R204 separation).** All eight triples $(S,K,U)$ are realizable for every $m\geq2$. Four successful installations can have exactly the same initial task outputs while $K$ and $U$ vary independently.

**Proof.** Set $G=\mathrm{id}$. Choose $C=\mathrm{id}$ for $S=1$ and a nonidentity permutation for $S=0$. Independently choose $F=\mathrm{id}$ for $K=1$ and a nonidentity permutation for $K=0$, and choose either value of $U$. The first successful action depends on $G$ and $C$, so fixing both at identity fixes all initial successful outputs while leaving $F$ and $U$ free. $\square$

This proposition is a finite possibility result. It neither asserts statistical independence in a population nor identifies the prevalence of any profile in people.

## 3.2 What an update probe can establish

For natural veridical feedback $z=G(a)$, the selected predictor state changes exactly when

$$
U=1\quad\text{and}\quad F(a)\ne G(a).
$$

Consequently, a natural null update is compatible both with an unused feedback writer and with an active writer receiving an already matched value. If the experimenter instead forces a known mismatch $z\ne F(a)$, a state change identifies $U$ **within this implementation class**. The inference requires a valid feedback port, a known pre-probe predictor row, a faithful post-probe readout of that same carrier, and the absence of an alternative writer or hidden gate. A changed output without these jointly satisfied premises is not the theorem's conclusion.

## 3.3 A comparator and a reflex can share every predictor-state trajectory

Compare two implementations. The first writes $z$ only when $U=1$ and $F(a)\ne z$. The second writes $z$ whenever $U=1$. If the value is already $z$, the second performs a write that leaves the stored value unchanged; the first performs no write.

**Proposition 2 (R204 implementation limit).** For every initial predictor state and every finite sequence of action/feedback pairs, the two implementations have identical predictor-state trajectories. Their write-event histories can differ.

**Proof.** At one step, both preserve the row if $U=0$ and both produce $z$ if $U=1$. In the matched case, omitting the write and overwriting with the existing value give the same next state. All other rows are unchanged. Induction gives equality for every finite sequence. A matched event with $U=1$ witnesses different write histories. $\square$

The result concerns a declared state projection. If the actual comparison operation or write event is separately instrumented, that larger observation may distinguish these implementations. Conversely, equal predictor-state histories cannot establish that a comparator operated, that a particular earlier source was retained, or that $H$ occurred. The reflex is not assigned an absence of experience; it is an organizational countermodel to an inference from an insufficient readout.

# 4. A physical source-and-consumer contract

## 4.1 Sources are carriers, not self labels

Fix $n\geq2$ distinct source registers $s_0,\ldots,s_{n-1}$ and two consumer ports. Each source has a binary value $x_i$. In the pure single-source class, fixed indices $a,b\in\{0,\ldots,n-1\}$ determine

$$
y=x_a,\qquad \widehat y=x_b,\qquad d=y\oplus\widehat y.
$$

The predictor is read before the consequence whose value is $y$. A common injective output encoding can replace the identity maps without changing whether the two outputs agree. The binary identity representation simply makes the protocol transparent.

The following premises hold together in the same contract: the named sources are independently addressable; their assignments are delivered as specified; each consumer has one fixed source; no hidden aggregation, alternative path, learning update, or route switch acts during the protocol; preparation is valid; and the agreement readout is faithful. Independent addressability is an intervention property, not a claim that naturally occurring source values are probabilistically independent.

In nominal trials all sources are yoked to a target $t$:

$$
x_0=\cdots=x_{n-1}=t.
$$

Every route allocation then gives $y=\widehat y=t$. Thus nominal success and alignment are identical for all $n^2$ allocations. With an identity forward table, every nominal target word also preserves the same forward-table state under either R204 writer. The diagnostic interventions below deliberately break this synchronization. They do not preserve successful task behavior or zero error on every probe.

## 4.2 A concrete active, passive, and remote comparison

For a three-source thought experiment, specify $s_0$ as a command register produced by a controller within a previously admitted bearer $B$; $s_1$ as an external apparatus's actuation register; and $s_2$ as a remote controller's command register. Their membership, generating processes, boundary crossings, and installed paths are fixed before examining success or any report.

A local route $(a,b)=(0,0)$, an externally driven route $(1,0)$, and a remotely driven route $(2,2)$ all give identical nominal outputs. The last has common-source prediction without an internal source; the middle has an internal prediction source without common-source actuation. R205 formalizes this independence as a two-source square between bearer-relative source locality and source correspondence [12]. Neither coordinate defines ownership or voluntary agency. Relocating an effector is also a different manipulation from relocating the command source.

These names organize an explicitly constructed installation. Source probing does not discover that a register belongs to a person merely because the register is numbered zero. Nor does intervening on its value preserve the natural process that originally generated that value. An actual experiment must record which claim concerns the unperturbed installation and which concerns a modified trial.

# 5. Exact protocols for pure routes

## 5.1 Observation fibers

Let an $r$-probe binary schedule be a matrix $X\in\{0,1\}^{r\times n}$. Its $i$th column is the codeword $c_i$. In each row, independently set the source values to that row of $X$.

If both outputs are available, the transcript is $(c_a,c_b)$. For any codeword $u$, let $E_u=\{i:c_i=u\}$. The set of installations producing a full transcript $(u,v)$ is exactly

$$
E_u\times E_v.
$$

If only disagreement is exposed, the transcript is

$$
D_X(a,b)=c_a\oplus c_b.
$$

The zero-disagreement fiber is therefore

$$
D_X^{-1}(0)=\bigcup_u E_u\times E_u.
$$

**Theorem 3 (SCU20261010-C2/C3).** A fixed binary schedule decides whether $a=b$ for every pair of pure routes if and only if all source codewords are distinct.

**Proof.** Distinct codewords make $c_a=c_b$ equivalent to $a=b$. Conversely, if $c_i=c_j$ for two different sources, installations $(i,i)$ and $(i,j)$ have the same all-zero disagreement transcript but different source-equality truth values. $\square$

The theorem identifies a predicate, not necessarily both source names. Disagreement is symmetric in $(a,b)$, so it cannot identify their order. Even unordered pairs can share a nonzero transcript: with four codewords $00,10,01,11$, the pairs $(0,3)$ and $(1,2)$ both produce $11$. Distinct codewords identify both roots only when both individual consumer transcripts are observed.

## 5.2 Optimal worst-case number of probes

**Theorem 4 (SCU20261010-C3).** For an unknown pair of fixed pure routes, exact universal same-source decision from binary disagreement readouts requires and is achieved by

$$
r_{\mathrm{pure}}(n)=\lceil\log_2 n\rceil.
$$

The lower bound also holds for deterministic adaptive protocols with zero error and that same readout.

**Proof.** A nonadaptive $r$-row code has at most $2^r$ different columns, so Theorem 3 requires $2^r\geq n$. Assigning distinct binary labels to the sources attains this bound. For an adaptive protocol, follow the branch on which every disagreement response is zero. Its interventions form a definite sequence of binary assignments. If fewer than $\lceil\log_2 n\rceil$ probes occur, two source columns coincide along this branch. Those unequal routes produce exactly the same zero responses as an equal-route installation, causing the same subsequent interventions and final decision. A universally correct decision is impossible. $\square$

This is a sensorimotor application of classical separating-system reasoning, with an explicitly restricted comparator readout [6,7]. It is not a new lower bound for general causal discovery, noisy sensing, arbitrary adaptive observations, or biological experimentation.

## 5.3 A known root changes the problem

**Theorem 5 (SCU20261010-C4).** If the actuator root $a$ is independently known, but the predictor root may be any source, one binary probe decides $a=b$ for all $n\geq2$: assign $x_a=0$ and $x_i=1$ for every $i\ne a$.

**Proof.** The actuator outputs zero. The predictor outputs zero exactly when it reads source $a$. With no probe, the nominal matched observations allow both $b=a$ and $b\ne a$, so a probe is necessary in this stated problem. $\square$

The same probe also works when the predictor ORs an unknown nonempty source set $J$: its output is zero exactly when $J=\{a\}$. This extension retains the known pure actuator root and excludes an empty constant-zero predictor.

The phrase “independently known” matters. Guessing the actuator root from a successful action would import the conclusion that the protocol is meant to establish. If prior evidence already decides both roots, no further probe is needed; that is a different information state.

For the three-source case, the following schedule suffices when neither root is known:

| Probe | Local source $s_0$ | External source $s_1$ | Remote source $s_2$ |
|:--|--:|--:|--:|
| 1 | 0 | 1 | 0 |
| 2 | 0 | 0 | 1 |

All nine route allocations match in nominal yoked trials. Under the schedule, disagreement $00$ means a common root within the pure-route class; $10$, $01$, and $11$ correspond respectively to the unordered pairs $\{0,1\}$, $\{0,2\}$, and $\{1,2\}$. The schedule does not establish which roots are biologically internal, whether a particular earlier command was used, or what the installation feels like.

# 6. Redundant consumers change the answer

Within this section, $A$ and $B$ denote source sets, rather than the consumer and bearer labels of §2. Let the actuator and predictor consume arbitrary nonempty source sets $A,B\subseteq N=\{0,\ldots,n-1\}$ by OR:

$$
y=\bigvee_{i\in A}x_i,\qquad
\widehat y=\bigvee_{i\in B}x_i.
$$

The target is now equality of the two installed OR source sets. It is not the number of reads that occurred in a particular short-circuit execution. The event implementation used here collects all specified inputs before aggregation, and distinguishes installed source lists from the actual ancestors of an output after a clamp.

## 6.1 A false positive from the pure-route code

For $n=4$, use columns $c_0=00,c_1=10,c_2=01,c_3=11$. Let $A=\{3\}$ and $B=\{1,2\}$. The aggregate predictor code is

$$
c_1\lor c_2=11=c_3.
$$

The two-bit protocol produces no disagreement even though the source sets are disjoint. Both installations also succeed and align under every nominal all-zero or all-one assignment. This is a counterexample to extending Theorem 4 beyond pure routes, not a violation of that theorem.

## 6.2 The exact universal cost for arbitrary OR sets

**Theorem 6 (SCU20261010-C5).** For $n\geq2$, exact universal decision of $A=B$ for arbitrary nonempty OR source sets, observing only binary disagreement, requires and is achieved by $n$ probes. Deterministic adaptation does not improve this worst-case bound.

**Proof.** The unit probes $e_i$, with source $i$ set to one and all others to zero, return disagreement exactly when $i$ belongs to the symmetric difference $A\triangle B$. All $n$ probes therefore decide equality.

For necessity, compare $(A,B)=(N,N)$ with $(N,N\setminus\{i\})$. The second pair is admissible because $n\geq2$. The two consumers disagree only at the source assignment $e_i$. Any correct fixed schedule must consequently contain every unit probe. For an adaptive protocol, follow its all-zero disagreement branch. The equal pair $(N,N)$ takes this branch, and the unequal pair $(N,N\setminus\{i\})$ takes it too unless $e_i$ is issued. Every $e_i$ must occur on that branch, requiring at least $n$ probes. $\square$

The singleton-row requirement is the extreme unrestricted-source case of familiar cover-free and superimposed-code ideas [8]. The useful contrast here is between two sensorimotor mechanism contracts under one observation interface. It is not a claim that all biological redundancy costs $n$ trials. Known sparsity, other aggregation laws, additional readouts, noise, and permitted intervention constraints define different problems.

\Needspace{10\baselineskip}

All rows below assume $n\geq2$, exact binary interventions, and the stated disagreement readout.

| Consumer contract and prior information | Decision target | Exact worst-case probes |
|:--|:--|--:|
| Two unknown pure roots | Same root? | $\lceil\log_2 n\rceil$ |
| One independently known pure root | Same root? | 1 |
| Arbitrary nonempty OR sets, $n\geq2$ | Same installed set? | $n$ |

# 7. What source probing still cannot identify

## 7.1 Root dependence is not all internal consumption

The R205 cancellation countermodel is stronger than a collision in a short code [12]. Work over $\mathbb Z_m$, $m\geq2$, with an external command $r$ and another source $b$. Compare a direct predictor $z=r$ with an implementation that actually receives two separately accessible branches $e_1,e_2$ and computes

$$
z=r+e_1-e_2\pmod m.
$$

Ordinary source interventions propagate $b$ to both branches, so $e_1=e_2=b$. The actuator and prediction are $(r,r)$ for every joint source assignment in both implementations. Nevertheless, changing one branch after the fan-out changes the cancellation predictor. Whole-source interventions have identified net dependence on source values; they have not identified every internal branch consumed by the installed computation.

This distinction generalizes the lesson of the OR counterexample without supplying a universal recovery theorem for arbitrary architectures. Exhaustive source assignments may determine a source-level input-output function, but many internal implementations can realize it. A branch intervention is a new physical intervention contract, not a clever relabeling of an old source observation.

## 7.2 Common ancestry does not identify the intake occurrence

Consider a root source feeding a shared relay register, which both consumers read. Compare it with the same root feeding two separate copies, one per consumer. Every source assignment gives identical actuator and predictor outputs. The installations differ in whether the consumers encounter one shared relay occurrence or two separate occurrences with common ancestry.

A node-write control performed before both consumer reads, with no intervening overwrite or compensation, distinguishes these two declared installations. Writing the actual shared relay carrier can change both outputs; writing the predictor's separate relay changes only its output. By contrast, replacing only the predictor's incoming edge can change only prediction in either installation. Thus node writes and edge substitutions answer different questions. Interpreting either observation requires prior identification of the carrier or branch that the intervention actually reaches.

![Source-level equivalence and carrier-level difference. Both installations copy the same source to the two consumers. The displayed targeted carrier writes distinguish the specified shared and separate relays under the timing and no-overwrite contract; an injection only on the predictor edge produces $(0,1)$ in both.](figures/source_resolution.png){width=95%}

The code records occurrence identities, chronology, and parent relations so this distinction is inspectable within the constructed model. The existence of that log is not evidence that a biological experiment has comparable access. Nor does the log define experience by an experimenter's observation. The physical relation, its formal description, and evidence for it remain different objects.

## 7.3 A sensory echo is not a pre-consequence predictor

A bypass can copy the actuator's consequence into a register after actuation. Its final two values agree for every source input just as a correctly routed predictor's values do. If the readout omits timing, the two cases share its signature. In the event model, audited timestamps distinguish a predictor read before actuation from an echo read afterward.

This control explains why predictive chronology is a premise. If an actual apparatus exposes only a final number called “prediction,” the name does not discharge the premise. Conversely, the temporal difference alone does not establish different agency, ownership, or $H$.

## 7.4 A complete clone is a different comparison

The counterexamples above preserve selected outputs, not complete physical organization. If a copy instead preserves the complete admitted structural type, C1 requires preservation of its corresponding complete experiential type [1,4]. Distinct occurrences can share a type; numerical identity and historical lineage are separate matters. One cannot demand opposite feelings from complete organizational clones as a validation condition for a C1-compatible bridge.

Likewise, a relabeling must transport source coordinates, their selected paths, transformations, temporal roles, and declared memberships together. Moving only the labels “internal” and “external” is not such a transport. Moving physical wires while keeping the port identities fixed is a changed installation.

# 8. Reproducibility and exact computational results

The companion package contains the English derivation, source contracts, claim ledger, negative controls, code, exact output JSON, source-reading receipt, and audit records. The main SCU program uses only the Python standard library. Its event simulator and its exhaustive optimization routine evaluate the problem separately: the optimizer constructs a finite set-cover instance for separating distinct source sets, without being given the analytic lower bound. It enumerates schedules until a cover is found. It verifies nonadaptive optima; adaptive lower bounds are established by the proofs above.

| SCU check family | Executed cases | Scope |
|:--|--:|:--|
| Nominal matched episodes | 406 | All pure route pairs, $n=2,\ldots,8$, both target bits |
| Coded pure-route episodes | 576 | Binary constructions for $n=2,\ldots,8$ |
| Zero-disagreement fiber cases | 5,045 | Every binary matrix through the minimal length for $n=2,3,4$, with all route pairs |
| Known-root episodes | 203 | All pairs for $n=2,\ldots,8$ |
| Shared versus separate relay comparisons | 256 | Every source assignment for $n=2,\ldots,5$ and each common root |
| Transported-coordinate comparisons | 256 | Declared cyclic source-coordinate transport |
| Nominal forward-state word comparisons | 1,116 | Binary words of length 0 through 4, all three-source routes and writer choices |
| OR source-set equality cases | 1,244 | All ordered nonempty set pairs for $n=2,\ldots,5$ |

The optimizer inspected 180,611 candidate schedules across eight finite searches, after excluding probes that separate no candidate pair. Its results were:

| Number of sources $n$ | Pure routes: exact minimum | Nonempty OR sets: exact minimum |
|--:|--:|--:|
| 2 | 1 | 2 |
| 3 | 2 | 3 |
| 4 | 2 | 4 |
| 5 | 3 | 5 |

The 5,045 matrix checks test the zero-disagreement/equal-column component. The full pair-output and nonzero-disagreement fiber formulas are established algebraically, rather than claimed as separately exhaustively tested.

The supplementary outputs also give the complete three-source route table, the OR false positive, the node/edge controls, and all eight inputs of the late-echo control. No reported case violates the declared equations. These counts refer to different kinds of checks; they are not added together as a sample size or number of independent experiments.

For provenance, R204 independently reproduced 28,096 finite model instances, 111,920 natural-feedback checks, 333,088 port relabel checks, and 6,776 rational mixture checks. Its saved comparator/reflex analysis covers 892 model pairs, with 118 cases having different write-event histories [11]. Concurrent R205 reports 608 single-read installations, 2,872 nominal matched episodes, 5,744 isolated-source probe episodes, 38,224 compensated recodings, 139 cancellation source assignments, and 1,288 branch probes [12]. These are inherited result counts, not newly added SCU participants. Reproduction commands and hashes distinguish original runs from this manuscript's reruns.

Two implementation corrections made during SCU review are retained in the failure record. A lazy OR evaluator initially allowed short-circuit reads while its event-parent list named every input; the revised event implementation explicitly collects all inputs. Also, installed source lists were initially liable to be confused with actual source ancestors after a node or edge injection. The revised log separates configuration from event ancestry and follows the latter through the executed parent graph. These repairs illustrate why a passing output table does not certify every semantic interpretation of a program variable.

# 9. Consequences for experience, intelligence, and self research

## 9.1 The positive UCT consequence is conditional and structural

If a faithfully identified source/consumer relation is part of the complete constitutive organization of an admitted actual token, C1 supplies its corresponding relation within that token's experiential organization. If a fully justified difference is a difference of complete structural type, the corresponding complete experiential types differ. A selected source graph need not be a complete signature, and the significance of a microscopic difference for a separately admitted macroprocess requires its own argument [1,3,4].

These statements provide a way to ask about organization *within* experience. They do not create an additional owner outside that organization. They also do not turn a selected route into a unique subject counter. Local actual processes are not deprived of their UCT status when they participate in a larger admitted process. A network of people carrying out an algorithm requires separate treatment of the people's continuing processes and of any admitted larger organization.

## 9.2 Four thought-experiment families

**Formation and ancestry.** Imagine a process acquiring a new command-to-predictor path. The source relation can change while the U1 status of the admitted process is unchanged. The construction concerns a form of organization; it does not reconstruct a real evolutionary transition or posit the first appearance of basal experience at the new path.

**Calculator and abacus implementations.** Hold the task law fixed while replacing direct electronic routing with registers, manual copying, or a mechanical relay. The protocol applies only if its addressability, timing, preparation, and consumer-class premises survive the change. Equal arithmetic answers do not establish that those premises hold. No substrate ranking of experience follows from the toy source counts.

**People implementing an agent.** Let participants move cards representing source values. A cancellation routine can require someone to read two cards even though the aggregate result has no dependence on their common value. Whole-source input-output probes therefore miss a real organizational distinction in this declared implementation. The participants' local processes and any larger admitted process remain separately specified; nominal algorithmic equivalence does not settle complete organizational identity.

**Copies, rewiring, and memory.** A relay copy can preserve every source signature while changing intake occurrences. A physical rewire can change which carrier a consumer reads. A complete type-preserving clone instead falls under C1's invariance. Copying a memory string or reproducing a current prediction does not, by itself, establish retention of one earlier source by the same continuing consumer.

These families are inherited from the research program [4,10]. Their role here is to test the exact protocol and prevent a convenient label from replacing an organizational premise.

## 9.3 An executable path toward an actual study

A study using these results should first select the organizational target: root equality, an OR source set, a particular branch's consumption, or an intake occurrence. It should then justify a mechanism class independently of the observations used to decide the target. For example, no amount of agreement under a pure-route code can establish the absence of an untested OR aggregator; the disjoint-set countermodel demonstrates why.

The study must next identify the actual ports and consumers, document the preparation and timing, specify the readout, and include a control that can fail the installation assumption. It can then apply the relevant protocol and report the remaining observation fiber. If the proposed endpoint is experiential, the endpoint and the bridge to it must be fixed independently of the target's desired result, allowing rival predictions and failure [2]. Reports may be one source of evidence; excluding them in advance or treating them as exhaustive would each require separate justification.

The immediate extension of this work is therefore a motor-command versus proprioceptive-consumer study with a stated target and instrument model, not an indefinitely enlarged list of synthetic sources. Agency, ownership, intensity, and sensitivity should be analyzed as distinct candidate endpoints. The present results constrain that study's inference; they do not supply its missing human evidence.

# 10. Limits, originality, and research status

The source-level theorems assume noiseless binary interventions, exact readout, fixed routes, and preparation. Finite reproduction checks do not establish those premises in a person, robot, or a currently deployed assistant. The general proofs cover all $n$ in their stated mathematical domains, but the enumerations cover only the reported finite ranges. No stochastic robustness bound, biological sample-size calculation, learning-drift theorem, or randomized bounded-error probe optimum is asserted.

The prior-art assessment is deliberately claim-specific. Classical separation accounts for the logarithmic labeling argument; cover-free codes account for the OR singleton requirement; UCT publications account for the basic correspondence, no-gate commitments, clone invariance, and behavior/organization distinctions. R204 and concurrent R205 remain named antecedents within the combined manuscript. The paper's claim is a focused protocol synthesis and its exact class-dependent applications. Priority for every possible equivalent formulation has not been established.

Independent review also found three errors in other pending records: R194's anchored parity-count statement omitted consistency between multiple anchors; R201 used an infeasible sharpness witness; and R202 allowed bounded conditional dependence while claiming an exact independence-based inversion. The companion corrections provide the missing anchor-consistency premise, feasible rational witnesses, and the appropriate residual-adjusted or set-valued interpretation. Those corrections do not support the source theorems above, and no proof in this paper depends on the faulty versions. Historical files are preserved and corrections are registered explicitly.

The completed map version remains UCT-MAP-v1.1.2. Candidate registration, a source-compatible manuscript, numerical checks, a whole-map compatibility review, and a new fully adopted map release are distinct statuses. The companion audit states exactly which statements, contracts, and affected derivations were read or reconstructed, and which historical proofs were reused. The open reviews concerning actual installation and independently anchored phenomenal targets are not self-closed by this paper.

# 11. Conclusion

Matched task behavior and prediction leave source relations underdetermined. Under an explicitly pure single-source contract, separating interventions close the same-root question with a logarithmic worst-case cost; independent knowledge of one root reduces that cost to one probe. Arbitrary OR aggregation changes the exact universal cost to one probe per source. Cancellation, relay copies, sensory echoes, and reflex writers show why even these successful organizational decisions must not be promoted into unrestricted claims about internal consumption, numerical continuity, comparator implementation, or a named experience.

The reusable result is a disciplined chain from an organizational target through a mechanism class and a valid intervention interface to a precisely limited conclusion. Within UCT, the corresponding experiential interpretation remains conditional on actual complete organization, without making basic experience contingent on successful prediction, control, intelligence, conceptual self, or report.

# References

1. Liu, H. *Unified Consciousness Theory I*, version 1.2. DOI: [10.5281/zenodo.23131575](https://doi.org/10.5281/zenodo.23131575). The source-reading receipt records the actual sections consulted.
2. Liu, H. *Unified Consciousness Theory II*, version 1.1. DOI: [10.5281/zenodo.23030320](https://doi.org/10.5281/zenodo.23030320).
3. Liu, H. *Unified Consciousness Theory III*, version 1.0. DOI: [10.5281/zenodo.23137088](https://doi.org/10.5281/zenodo.23137088).
4. Liu, H. *Experience, Intelligence, and Self Within Experience: Definitions, Conditional Theorems, and Thought Experiments for a Structural Account*, TA25, version 1.0. DOI: [10.5281/zenodo.23206492](https://doi.org/10.5281/zenodo.23206492).
5. Zaadnoordijk, L., Besold, T. R., and Hunnius, S. (2019). A match does not make a sense: on the sufficiency of the comparator model for explaining the sense of agency. *Neuroscience of Consciousness*, 2019(1), niz006. DOI: [10.1093/nc/niz006](https://doi.org/10.1093/nc/niz006).
6. Bollobás, B., and Scott, A. (2007). On separating systems. *European Journal of Combinatorics*, 28(4), 1068–1071. DOI: [10.1016/j.ejc.2006.04.003](https://doi.org/10.1016/j.ejc.2006.04.003). [Author manuscript dated 18 April 2006](https://people.maths.ox.ac.uk/scott/Papers/separating.pdf).
7. Shanmugam, K., Kocaoglu, M., Dimakis, A. G., and Vishwanath, S. (2015). Learning causal graphs with small interventions. *Advances in Neural Information Processing Systems 28*. [arXiv:1511.00041](https://arxiv.org/abs/1511.00041).
8. D'yachkov, A., Rykov, V., Deppe, C., and Lebedev, V. (2014). Superimposed codes and threshold group testing. [arXiv:1401.7485v1](https://arxiv.org/abs/1401.7485v1). The source is used for the cover-free definition and singleton-row condition, not for a new claim about their history.
9. Ganesh, G., Nakamura, K., Saetia, S., Mejia Tobar, A., Yoshida, E., Ando, H., Yoshimura, N., and Koike, Y. (2018). Utilizing sensory prediction errors for movement intention decoding: A new methodology. *Science Advances*, 4(5), eaaq0183. DOI: [10.1126/sciadv.aaq0183](https://doi.org/10.1126/sciadv.aaq0183). The prior-art claim here is limited to the primary abstract and indexed experimental description.
10. Liu, H. UCT research records IA20261008, R147, R174, R182, R192, and RTTH20261009, as located in the versioned source and coverage receipts accompanying this manuscript. These records establish important earlier organization, consumer, copying, and labeling results. Repository: [thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord/tree/8bac31cc0b9fb4c70d87f688dabbadeb6166addb/research/uct-agent-consciousness-workspace).
11. Liu, H. *Sensorimotor alignment and use*, R204, SAU-RESULT-v0.2.0, 10 October 2026. [Pinned research record](https://github.com/thechurchofagi/trinity-accord/tree/90a542d697d923aa484f2bd5a4484a438125325a/research/uct-agent-consciousness-workspace/records/R204_SENSORIMOTOR_ALIGNMENT_AND_USE_20261010).
12. Liu, H. *Action sources, actual consumers, and the limits of matched prediction*, R205, ASC-RESULT-v0.1.0, 10 October 2026. [Pinned concurrent research record](https://github.com/thechurchofagi/trinity-accord/tree/a22ad487b2a072293de2ecb55b4f2cc2a2c0dafc/research/uct-agent-consciousness-workspace/records/R205_ACTION_SOURCE_CONSUMER_CORRESPONDENCE_20261010).

13. Liu, H. *Task-Relative Continuity Through Changing Representations: Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout*, RTTH20261009, version 1.0.0. DOI: [10.5281/zenodo.23251651](https://doi.org/10.5281/zenodo.23251651).
14. Liu, H. *Actual Participation Before Counterfactual Capacity: A Token-Level Constraint on Conscious Organization*, TA-TR-2026-18, version 1.0. DOI: [10.5281/zenodo.22991126](https://doi.org/10.5281/zenodo.22991126).

## Data and code availability

The companion record is `records/SCU20261010_Source_Consumer_Protocols/` at the pinned repository commit above. The same DOI supplies `reproducibility-v1.0.1.zip`, containing the six-job reproduction runner, frozen code and results, claim and source contracts, negative controls, selected audit records, and the internal release review. `check_source_consumers.py` produces the SCU exact-result file and route table. The supplied manifest pins the bundled bytes; the complete record and historical navigation remain in the repository. R204 and R205 retain their credited original record paths and are also bundled as frozen reproduction inputs. This selected supplement is not a complete repository backup. No participant data were collected.

## Review disclosure

The manuscript, proofs, code, scope, and prior-art account were developed and checked with AI assistance. Parallel checking is documented as an internal review workflow, not as independent human peer review. External publication, phenomenal validation, and completed-map adoption are not implied by the manuscript's version number.

