# When One Signal Is Many Occurrences: An Interface-Relative No-Go for Causal Multiplicity

**Research ID:** R187-20261009 · **Result:** CMA-RESULT-v0.1.0 · **Map candidate:** UCT-MAP-v1.1.2-R187-candidate.1  
**Author:** Hongju Liu · **Date:** 2026-10-09 · **Status:** New scoped project-level synthesis and formal countermodels; **PENDING_MAP/AUDIT_INCOMPLETE**; not peer reviewed, no publication decision.

## Abstract

Physical relations may occur once yet participate in several organized processes, or may occur multiple times while synchronized to identical values. Identical reports do not establish the numerical identity of those occurrences. We sharpen this prior distinction by separating **temporal test insufficiency**, **interface-level structural nonidentifiability**, and **insufficient fidelity of constituent-specific interventions**. A controlled bisimulation lemma implies that no adaptive behavior-only policy, however long, distinguishes related realizations under a fixed observable action alphabet. A concrete shared-source/diagonal-copies witness makes the physical-multiplicity ambiguity explicit. When the intervention family and readouts are independently certified, a selective-write contrast can distinguish a restricted shared-bit model from a two-copy implementation; its exact two-readout Euclidean separation is `|delta|/sqrt(2)`, giving a two-sided bounded-error exclusion rule. Under a separate Bernoulli synchronization-leak example, the sharp equal-prior discrimination error after T trials is `(1-p)^T/2`; for p=0 the ambiguity is permanent under the interface. Countermodels show why independent coordinate control, high response rank, or an off-diagonal output do **not** themselves count actual occurrences: one multibit physical occurrence and downstream branch modifiers can emulate them. This paper's algebra and bisimulation tools are classical. The scientific contribution is a source-aware, explicitly falsifiable evidence-boundary synthesis for cross-scale physical occurrence claims in the UCT research program, not a new consciousness law or proof of experiential identity.

## 1. Research problem, antecedents, and why this is not a new experience gate

This study continues `R185` (cross-scale shared actual occurrence vs synchronized copies), `R186` (arbitrarily deep finite-length hidden interactions), `OL20261009` (physically anchored observable write-gap), and `CM20261009` (compensation can hide causal effects). The author-side completed effective map at the start was `UCT-MAP-v1.1.1`, 804 nodes/387 rule records/228 contextual links: 1,419 total review items. R185, AC, IL, R186, UI and CM remained separately pending. Their pending claims are consulted as research targets, not imported as discharged premises.

UCT's C1 is the conjectural identity of actual physical process organization and experiential structure; U1 gives nonempty basal experience for every independently admitted actual process, and P3 protects any local process which actually continues to exist. This study neither validates C1 nor changes it, and it never uses integration, intelligence, report or an observer's count of nodes as a threshold for experience. A conditional inference about one physical occurrence versus two is not an inference about one versus two exclusive subjects, felt unity, the phenomenology of agency or the number of experiences.

We distinguish four types: **occurrence** (physically traced event with bearer/time/mechanism), **membership** (participation of that occurrence in one or more actual process tokens), **interface behavior** (results under particular available actions and readouts), and **phenomenal comparison** (only with UCT's complete-instance premises). Neither equal values nor a map's drawn edge discharges an occurrence-identity fact.

## 2. Fixed experiment contracts

Model a controlled, discrete-time state machine by a state space `S`, action alphabet `U`, transition `T_u:S -> S`, and observation `O:S -> Y`, with fixed initial state. A policy may adaptively choose the next input, including randomization, from the observed interaction history. We require the **same physically interpreted action labels** and **comparable calibrated outputs** across hypotheses. Merely giving two different mechanisms the same English label does not create a shared intervention contract.

A relation `R` between states of two model classes is a **controlled observational bisimulation** for this purpose when, for every `(s,t) in R`: (i) `O_A(s)=O_B(t)` under the same readout contract; (ii) `T^A_u(s) R T^B_u(t)` for each common admissible `u in U`. Stochastic versions require equal output kernels and a transition coupling that stays in R under each common action. The action alphabet, actuator physical attachment, clock, data collection, fidelity, and relevant compensation must be independently justified before the abstract semantics can be applied to a patient, organism, prosthetic system or active AI device.

### Proposition 1 — all-policy indistinguishability under a fixed interface

For related initial states and the bisimulation contract above, **every** finite transcript has the same probability under the two models for **every** policy based solely on prior interface observations, even if that policy uses unlimited computation. For deterministic machines, this holds as literal equality of histories. For stochastic kernels it holds as equal laws. Thus with equal model priors, optimal binary decision error remains exactly 1/2 for every test length. Under the induced cylinder distributions this also covers infinite transcripts for which the process law is determined by its finite-dimensional marginals.

**Proof.** At time 0, observations match. Coupling policy randomness, a shared history induces the same next action; by the transition-closure condition, resulting states remain related. Their subsequent observations match; induction closes every finite history. The stochastic version couples transitions in R and uses equal emissions; integration of the coupling gives the same law. Equal likelihoods make no test superior to chance under equal priors. This is a direct use of standard bisimulation, not a new theorem of transition systems.

### Thought experiment — one actual source, or m synchronized sources?

World `S`: one binary occurrence-locus `s`, two or more non-invasive faithful observers all read the same `s`; the only intervention is the global `c in {0,1}`, with `s <- s xor c`. World `C_m`: `m` physically distinct binary occurrence-loci `a_1,...,a_m`, all initialized to the same bit and each updated by the same common global `c`: `a_i <- a_i xor c`. Observers see `(a_1,...,a_m)`. The relation `R={(s,(s,...,s))}` is a bisimulation; there may be 1 or m distinct physical occurrence-loci while their entire available observed histories match.

This toy model stipulates event identities; it does **not** physically prove that such a toy architecture has any particular experiential multiplicity. Shared **occurrence count** differs from **token membership count**. The result is stronger than R186's finite-horizon blindness: increasing observation length alone cannot break this interface-induced equivalence while the permitted action family remains common-mode.

## 3. The positive route, and the port-circularity trap

Suppose the copied world has an independently justified native port that can change **only the first physical occurrence-locus** before a faithfully calibrated, simultaneous readout, and its synchronizer is demonstrably not applying a compensating re-write within that window. A bit flip from `(s,s)` to `(1-s,s)` is then outside the reachable observation set `{(t,t):t in {0,1}}` of the restricted single-binary-source model equipped only with unmodified faithful readout channels. That observation **rejects the restricted shared-source hypothesis under the port/clock contract**.

But this is not an automatic comparison of like-for-like actions: a genuinely single source cannot be commanded to take two distinct intrinsic bit values at once. The instrument's constituent-selective access is itself extra independent evidence about the hardware; it may embody exactly the duplicate-locus premise one is trying to prove. The contrast therefore relies on the external certification of the addressed physical bearer. Calling an instruction `do(left)` in both diagrams without mapping its location does not satisfy the common-instance contract.

**Countermodel A (synchronizer).** The copied system may reset its second locus to the first before sampling, producing equal observed values despite two distinct loci. An 'absence of difference' then does not prove sharing.

**Countermodel B (branch modifier).** One binary shared source `s` with a separate *downstream readout-edge* modifier can display `(1-s,s)` without creating two intrinsic source occurrences. The observed off-diagonal tuple alone therefore does not prove duplicate sources. A trace must distinguish a source write from an edge/readout rewrite.

**Countermodel C (single multibit source).** A single physically treated process occurrence can have several independently variable internal coordinates. A response matrix of rank 2 need not imply two separately identifiable physical occurrences, much less two experiential owners. Conversely, copied sources restricted to diagonal common-mode actuators yield rank 1. **Rank counts accessible linear directions relative to admitted ports, not occurrences or experiences.** The choice of process granularity itself needs source-specific definition and causal provenance.

## 4. Exact finite-horizon and bounded-noise contrast

With two calibrated continuous readouts, if the copied hypothesis under a truly source-specific write predicts `y_C=(s+delta,s)` while the faithful single-source comparison can select its best common-mode response `y_S=(t,t)` (allowing arbitrary real `t`), then

`min_t ||y_C-y_S||_2 = |delta|/sqrt(2)`, attained at `t=s+delta/2`.

**Proof:** minimize `(s+delta-t)^2+(s-t)^2`, whose unique stationary point is `t=s+delta/2`; the minimum square is `delta^2/2`. The `t` choice grants the shared hypothesis maximal freedom to imitate the two outputs. With independent worst-case readout error bounds `||n_C||_2<=epsilon` and `||n_S||_2<=epsilon`, the resulting data balls cannot overlap if

`|delta|/sqrt(2) > 2 epsilon`.

At equality the balls touch and the strict rejection condition does not hold. Any unknown adjustment of readout branches, changing instruments, or compensator channels changes the admissible comparison class and must be added before claiming this separation. This is classical Euclidean projection/OL mathematics applied to a stricter causal bearer contract, not a new universal index of consciousness.

## 5. Exact distinction: fundamental interface masking versus small statistical leakage

A useful failure control permits copied-world synchrony to fail rarely, making one observed report differ from its peer with independent probability `p` at each **truly comparable and reset** trial; the exact shared model deterministically shows no discrepancy. With T reset trials, the optimal equal-prior binary classification error is

`R_T^* = (1-p)^T/2`.

The optimal test announces the copied world if any mismatch is observed. Under the shared hypothesis that event never occurs; under the copy hypothesis the probability of no mismatch is `(1-p)^T`. The total-variation distance between transcript laws is `1-(1-p)^T`, proving the sharp risk formula by the classical two-point testing identity.

When `p=0`, no number of trials discloses multiplicity through this interface. When `p>0` and independent resets are genuinely feasible, evidence eventually accumulates. This is **not** evidence that natural synchronized duplicates have independent leak probability p, nor a biological sample-size forecast. Without the reset/independence assumptions and fixed trial definition, this risk formula does not apply.

More generally, if one can establish a conditional coupling under a common adaptive-policy history that fails with probability at most `eta` per step, then the transcript law TV is at most `1-(1-eta)^T<=T eta`; under equal priors, error is at least `(1-min(1,T eta))/2`. This is a conventional coupling/Le Cam bound whose premisses cannot be inferred from high correlation alone.

## 6. The crucial cross-episode inference limitation

A selective write or the act of clamping a synchronizer **changes the physical process organization during that intervention**. If a claim concerns a relation occurrence **in the earlier undisturbed episode**, one cannot simply transfer an observed post-intervention event count back to the earlier episode. This requires a justified persistence/lineage link and a specification of how the intervention maps the original bearer into the modified process. It is a noncircular experimental identity problem, not a challenge to the ability to perform interventions.

In particular: (i) the existence of two addressable electrical contacts at t1 is not proof that the corresponding two previously hypothesized relation **occurrences** at t0 were separately instantiated; (ii) demonstrating a previously unmeasured hidden branch under selective perturbation excludes a specified hardware model but does not identify an experiential owner; (iii) an invasive experiment might alter the very UCT structure one later describes. For the last inference, C1's conditional structural correspondence must use the *appropriate actual post-intervention* token and its signature, not silently the previous one.

This is a **limit on inferential transfer**; it does not deny that a sufficiently rich independent physical trace, anatomy, time-resolved recording, and non-destructive evidence could ground a pre-episode attribution. The burden is concrete, rather than categorically unknowable.

## 7. UCT interpretation and relation to established theory

Under UCT's unverified C1/U1/P3 commitment, if each selected physical process token is independently actual, its experience does not require a complex-agent ability, self-report or uniqueness criterion. If a local process actually persists within a larger token, its experience remains nonempty without claiming its content unchanged. `m` distinct copied signal events do not automatically imply m phenomenal **subjects**, and `m` scale memberships of one event do not multiply the event. Complete type inferences require independently validated bearer identity, complete organizational signature and comparison-invariant difference; current finite automata have not supplied these.

These results should not be construed as UCT predictions that IIT, GNW or self-model theories cannot accommodate. IIT 4.0 explicitly takes a contrasting maximum/exclusion approach to which physical complexes support experience; UCT's basal-experience commitment is a contested theoretical axiom, not experimentally validated by the above tests. Metzinger's self-model theory distinguishes a functional representational self from a phenomenal first-person perspective; our tests settle neither.

**Novelty boundary:** R185 already identified shared/copied value-level ambiguity and synchronizer effects. TA25 already demonstrated perfect self-prediction under wrong attachment and the role of actual assembly. `OL` provides projection gaps, `CM` addresses compensated hidden effects, and `R186` provides arbitrarily deep finite testing blind spots. The narrower current addition is the **all-adaptive-policy no-go in a fixed common intervention language, together with a clear separation from finite statistical leakage, physical-port asymmetry, invasive-lineage obligations, and explicit countercontrols**. It is a stronger articulation of when an occurrence claim is testable, not a new structural theorem of probability, automata or consciousness.

**External antecedents verified (representative; not exhaustive):** Givan, Dean & Greig (2003), *Equivalence Notions and Model Minimization in Markov Decision Processes*, DOI `10.1016/S0004-3702(02)00376-4`; Shpitser & Tchetgen Tchetgen (2016), *Causal Inference with a Graphical Hierarchy of Interventions*, DOI `10.1214/15-AOS1411`; Squires et al. (2023), *Linear Causal Disentanglement via Interventions*, arXiv `2211.16467`; Orujlu et al. (2026), *Partially Observed Structural Causal Models*, PMLR 337:5111–5137 (UAI 2026); Nguyen et al. (2021), *Sensorimotor Representation Learning for an Active Self in Robots*, DOI `10.1007/s13218-021-00703-z`; Tononi et al. (2023), *IIT 4.0*, DOI `10.1371/journal.pcbi.1011465`. Readback scope: abstracts and relevant methods/results, not an exhaustive claim-by-claim proof comparison of all cited texts.

## 8. Reproducibility, status, and next test

The exact pure-Python/SymPy checker enumerated 8,184 finite common-mode input histories over m=2,3,4,5 (all lengths up to 9 and both initial bits), six accessibility rank cases, selective intervention/masking/branch controls, exact 2-readout projection checks, and 78 exact stochastic TV/Bayes-risk cases; see `check_models.py` and `TEST_RESULTS.json`. Enumeration of adaptive policies was NOT performed: Proposition 1 is proved by the bisimulation argument, and numerical tests cover open-loop histories only. No human, animal, actual agent consciousness or phenomenological measurements occurred.

The research is a substantive scoped negative/identification-boundary result but **not yet ready as a strong standalone consciousness paper**: much mathematics is classical and the exact experimental bearer/port/lineage contract has no actual validation. Candidates for a scientific application include virtual retina/gene-regulation interventions, prosthetic closed-loop wiring and duplicated AI inference engines with trustworthy hardware tracing. A useful next step would specify one existing actual system's source identity, surgical intervention target and synchronizer before measuring, and show a falsifying result over matched conditions, not infer subjective feeling from output.

Current completed map remains `UCT-MAP-v1.1.1`. This is `R187-CMA-v0.1.0` under a **PENDING_MAP / AUDIT_INCOMPLETE** increment until exact v1.1.1 effective map + 1,419-item semantics are fully reviewed and affected derivations rechecked; existing R185/AC/IL/R186/UI/CM remain pending. No DOI, journal submission, OTS or Arweave action was authorized or taken for this research result.
