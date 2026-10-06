# R126 — From constitutive identity to a justified causal description

Hongju Liu / UCT research checkpoint, 6 October 2026.

**Scope:** analytic continuation under the fixed published UCT commitments. No new biological fit, AI benchmark, simulation, experience label, or publication release. The arguments below are hand-derived, not machine-verified proofs. They are not claimed as historically new general mathematics.

## 1. Why theory resumes

The user's screenshot restates the R106 root map: experience, intelligence, behavior and report are distinct objects anchored in the same actual organization. R120 consolidated the conditional implications. R121 then classified basic implications as closed and recommended empirical T2 completion as the next priority. Its statements that the remaining support correspondence was no longer a theory gap, and that further theory had low marginal value, were too broad.

Closing a few implications does not finish the theory of which selected physical relations support a capability, which summaries preserve their dynamics, or which physically justified substructures license selected experiential interpretation. R120 explicitly assumed justified projections and actual constitutive anchoring; it did not derive a general procedure establishing those assumptions. Paper C §6.4 and Appendix E already warn that predictive closure, complete-type identity and sensory coordinates are different claims.

The user's 2026-10-06 direction now supersedes the empirical-first queue: continue first-principles theory before designing further empirical work. R122–R125 remain preserved as scoped evidence. They neither establish nor refute C1.

## 2. Keep the types of objects explicit

Fix an actual valid process token P, its interval tau, an appropriate common complete signature, and the relevant comparison conditions. Write k(P) for the complete structural type and e(P)=Phi(k(P)) for the complete experiential type. Under C1, Phi is an identity correspondence at the complete-type level; it is not an independently fitted decoder.

| Object | Formal role | Important qualification |
|---|---|---|
| Complete experience e | Experiential presentation of complete actual k | C1 is the fixed internal premise here. |
| Capability J_M(k) | Task/resource/boundary-relative capability profile or law | It is not a single sampled score, and must actually be well defined on this type domain. |
| Behavior B_C(k) | Output law under declared context and horizon | Different sampled actions alone do not imply different complete types. |
| Report R_C(k) | A specified output/access law | Report is normally a kind of behavior, not an independent substance. |
| A measured coordinate p | A function used to describe or estimate some distinctions | Its existence as a function does not establish an actual biological subsystem. |
| Causal model state s | A sufficient state in a separately supplied dynamical model | An observed neural vector must not silently be assumed sufficient. |

Thus the screenshot's non-equality symbols express non-identity of concepts and generally different information content. They do not state statistical independence or assert that every numerical value must differ.

The established fixed-comparison implication remains:

    J_M(k1) != J_M(k2)  =>  k1 != k2  =>  Phi(k1) != Phi(k2).

Equality of capability does not support the reverse implication without the required identifying conditions. These are already Paper C/R106 results, not newly discovered in R126.

Likewise, a dormant ability is not the actual execution of every task the architecture could perform. Program specification, physical storage, current inference, and a continuing scaffolded interaction are different comparison objects. An actual physical storage process is not denied experience under U1; its existence does not actualize every counterfactual execution. Paper C §4.1 already supplies this distinction.

## 3. Proposition 1 — Induced commutation is automatic and cannot select content

Let S be the admitted complete structural-type domain and E=Phi(S), with Phi:S→E bijective as required by complete-type identity. Take any function p:S→Z. Define

    p_E = p o Phi^(-1) : E→Z.

Then

    p_E o Phi = p.

**Proof.** For every k in S,

    p_E(Phi(k)) = p(Phi^(-1)(Phi(k))) = p(k).

No further property of p was used. QED.

**Consequence.** If the experiential projection is defined solely by transporting the chosen physical projection through C1, commutation holds for every projection. The equation alone cannot establish that p:

- is an actual constitutive sub-process rather than an analyst's summary;
- is causally sufficient for a capability;
- identifies a particular phenomenal coordinate;
- establishes one unified subject or an exclusive boundary.

This does not invalidate R120 Bridge I, which also assumes a physically justified selected constitutive mapping. It identifies why that additional assumption cannot be discharged by writing a commuting diagram. An independently specified experiential target would change the problem; its bridge cannot simply be defined after selecting p.

No experience-existence threshold is introduced. Actual simple, sparse, overlapping and nested processes remain within the published UCT domain. The issue is what a particular mathematical description establishes about an actual process.

## 4. Proposition 2 — Exact causal-state closure requires within-class agreement

This proposition concerns a supplied physical/mechanistic model, not C1 alone. Distinguish its instantaneous state s from the complete type k of an actual process episode.

Assume:

1. A finite nonempty state set Omega is causally sufficient for the declared model, including all relevant memory, delays and boundary inputs.
2. A finite family A of labeled, physically interpreted operations has total deterministic updates F_a:Omega→Omega.
3. A selected coordinate p:Omega→Z has Z=p(Omega).
4. Relevant outputs are represented by r:Omega→Y. Y may itself be a space of specified output probability laws.

There exist maps Fbar_a:Z→Z with

    p(F_a(s)) = Fbar_a(p(s))   for every a and s

if and only if

    p(s)=p(t)  =>  p(F_a(s))=p(F_a(t))   for every a.       (C)

In addition, an output map rbar with r=rbar o p exists if and only if

    p(s)=p(t)  =>  r(s)=r(t).                              (O)

**Necessity.** If a descended map exists, equal arguments p(s)=p(t) must have equal images under that map. The same reasoning applies to rbar.

**Sufficiency.** For z in Z, choose any s with p(s)=z and set Fbar_a(z)=p(F_a(s)). Condition (C) makes the answer independent of the representative. Condition (O) similarly defines rbar(z)=r(s). QED.

If these conditions hold for every declared operation, induction proves correspondence for every finite sequence of them and for the associated output laws. A baseline output match or a correlation coefficient cannot replace (C).

**Ports and domain are part of the assumptions.** A natural input, an internal reset and a pathway inhibition are different labels unless a physical mapping justifies their identification. If operations are partial, availability must also be constant within each summary class; one must preserve enabledness rather than silently applying impossible operations. The theorem can then be stated on shared admissible domains or with an explicit disabled marker. The finite proof below uses total maps to avoid hiding that extra condition.

For a supplied finite Markov model, the corresponding condition equates the pushed-forward next-summary probability laws within each class, for each operation. The pointwise deterministic condition must not be imposed as a universal noise-free law of biological recordings.

This is the familiar quotient/congruence condition. Paper C §6.4 already proves the related capability-class closure criterion for a transmission kernel. R126 applies the distinction explicitly to selected within-process state, output and operation descriptions. It does not rebrand lumpability as a new UCT theorem.

## 5. Proposition 3 — Hidden within-class disagreement imposes an error floor

Give Z a metric d. For a fixed operation a and summary z, define

    Delta_a(z)
      = max{ d(p(F_a(s)), p(F_a(t))) : p(s)=p(t)=z }.

The maximum exists because Omega is finite. For any deterministic summary-only predictor g_a:Z→Z,

    max_{s:p(s)=z} d(g_a(z),p(F_a(s))) >= Delta_a(z)/2.    (L)

**Proof.** For any s,t in the class, the triangle inequality gives

    d(p(F_a(s)),p(F_a(t)))
      <= d(p(F_a(s)),g_a(z)) + d(g_a(z),p(F_a(t))).

At least one of the two errors is at least half their distance. Maximize over the pair. QED.

Thus a uniform error requirement epsilon needs Delta_a(z)<=2 epsilon for every class and operation. That condition is necessary; it is not sufficient in an arbitrary metric space with a constrained prediction range.

This is a structural information limitation: changing the predictor cannot recover distinctions already merged by p. It motivates either refining the represented state or explicitly restricting the claimed domain/tolerance. The bound is a worst-case statement about a supplied model. It is not a bound on average cross-validation loss and cannot be numerically read off R125's rat summaries. Observation noise can require a distributional state/observation model; the proposition does not identify such a model.

## 6. Proposition 4 — A finite model admits a least required refinement

Given the finite deterministic setup, start with the equivalence

    s ~0 t  iff  p(s)=p(t) and r(s)=r(t).

Refine recursively:

    s ~(n+1) t
      iff s ~n t and F_a(s) ~n F_a(t) for every a in A.

Let b0 be the initial number of classes and N=|Omega|.

**Claim.** There are at most N−b0 strict refinements. At stabilization, ~* is the coarsest operation-stable equivalence refining ~0. Its quotient has well-defined updates and the declared outputs.

**Proof.** Each step is an equivalence relation refining the previous one. A strict refinement increases the number of classes by at least one; it cannot exceed N. At a fixed point, equal classes have equal successor classes under every operation, so Proposition 2 applies.

To show minimality, let ≈ be any operation-stable equivalence refining ~0. Inductively assume ≈ refines ~n. If s≈t, then s~n t and F_a(s)≈F_a(t), hence F_a(s)~n F_a(t) for every a. Therefore s~(n+1)t. Consequently ≈ refines every stage and ~*. QED.

This characterizes the least extra distinction structure required within this supplied finite model and declared operation/output family. It does not identify the actual model from observations, guarantee finite state for a brain, or specify the unique sufficient state of every implementation of the same task. Refinement algorithms have established prior art; no new efficient algorithm or complexity improvement is claimed.

Adding distinctions can restore a causal description without making it complete constitutive organization. A quotient sufficient for selected outputs and interventions is still relative to that selected family. Even complete closure on that family does not establish a unique subject or complete experiential identity.

## 7. Three claims that must stay separate

| Claim | What is required | What it does not establish by itself |
|---|---|---|
| A descriptive/decodable coordinate exists | A function or estimator and its measurement conditions | A sufficient dynamical state |
| A selected causal-state description closes | A justified model, class agreement, outputs, operation domains and temporal interpretation | An actual distinct sub-process or complete experiential type |
| A selected constitutive experiential interpretation is warranted under C1 | Actual support, justified process/substructure boundaries and a source-faithful constitutive relation | A familiar feeling label, exclusive subject, scalar richness or valence |

The last row is a research obligation, not a newly imposed gate on experience. The existence of an actual valid process and the validity of one proposed coarse description are different questions.

Under complete C1 identity, causal changes in actual constitutive relations have their corresponding experiential interpretation. It is not legitimate to add an independent knob that deletes E while leaving complete K fixed. It is equally illegitimate to infer an independently existing experience-bearing subsystem merely from an arbitrary coordinate of K.

## 8. What this changes about R125 and the research sequence

R125's D(n_t) was a specific learned observation coordinate tested against a unit-gain update. Its failure constrains that candidate. It does not imply that complete biological organization lacks an accumulation mechanism, that experience is absent, or that C1 is false. Conversely, a successful decoder would not have discharged the constitutive premises above.

The theoretical tasks now have priority:

1. Define the actual bearer, episode, boundary and comparison family.
2. Derive which retained distinctions and causal availability a selected capability requires; preserve alternatives and background conditions.
3. Determine whether the selected state description is closed under the intended inputs and internal operations, and what refinements are required.
4. Justify the passage from a causal description to an actual constitutive substructure before making the conditional experiential statement.
5. Specify what observation would discriminate remaining theoretical alternatives, then design an empirical test suited to that distinction.

These are local readiness conditions for a chosen question, not a demand to solve all consciousness theory before any empirical work can ever occur. Experiments remain useful for selecting among physically possible organizations; uncertain measurements cannot settle an ill-specified theoretical target.

No new experiment is launched or queued by this checkpoint. The next theoretical focus is the actual support/boundary justification in items 1–4, starting from one capability and allowing external memory/scaffold relations when they are actually constitutive. Functional dependence alone is not sufficient to infer membership or one unified subject.

## 9. Claim audit and correction of overstatement

| Statement | Assessment |
|---|---|
| Basic projection implications in Paper C/R106/R120 are finished deductions | Retain within their fixed assumptions. |
| Therefore all worthwhile theoretical work is finished | Withdraw; it does not follow. |
| A transported projection commutes with C1 | Algebraically automatic; not evidence that selects a phenomenal target. |
| Every decodable coordinate is a causal state | False without the closure conditions. |
| Every causal quotient is an actual unified subject | Not established; no such theorem is asserted. |
| R125 failed point maps refute UCT | Invalid inference. |
| R126 supplies new empirical evidence | No; this is analytic work. |
| The general quotient/refinement mathematics is historically original | Not claimed; prior art is explicit. |
| R126 completes the constitutive-substructure bridge | No; it exposes and sharpens the remaining obligation. |

For continuity, the canonical T2 clause meanings remain those of R119: C0 grounding, C1 baseline behavior, C2 transition, C3 intervention transport, C4 time, C5 nuisance stability, C6 anti-triviality/mapping discipline. R125's shorthand attached state identification to C1, shared-output-law mismatch to C5 and replay to C6; those observations must be interpreted under the original definitions, not as replacements for them. This corrects certificate labeling, not the saved numerical results. UCT axiom C1 is a different object from T2 checklist clause C1.

## 10. Sources and originality boundary

- Published UCT III v1.0: §4.1 (actual execution), §6.4 (closure and its limits), §11 (identity and causal interpretation), Appendix E (complete-type versus sensory-coordinate distinctions).
- R106: complete first-principles map; R120: bridge schema and its conditional projections; R121: complete closure audit and the empirical-first recommendation being revised.
- R119: canonical T2 definitions and selected operation mapping. R125: preserved selected-map findings, not a new execution in this round.
- Rubenstein et al. (2017), [Causal Consistency of Structural Equation Models](https://arxiv.org/abs/1707.00819). The author abstract was checked for the existing intervention-consistency framework; this round does not claim a full-text literature audit.
- Paige and Tarjan (1987), [Three Partition Refinement Algorithms](https://doi.org/10.1137/0216062). Publisher/institutional search metadata establishes relevant algorithmic antecedents; the Princeton full-page request failed with HTTP 403. No claim that this round read their complete proof or reproduced their optimized algorithm.

The contribution of this checkpoint is a corrected priority, an explicit audit of an under-justified inference, and a connected set of sufficient/necessary conditions with proofs and limits. It is not a new physical law of consciousness or a completed constitutive identification theorem.
