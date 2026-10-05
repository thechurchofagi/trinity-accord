# R86 — Fission contrast identifiability and consequence-belief gating

Hongju Liu / UCT agent-consciousness research. 2026-10-06. Formal design note with exact finite checks. This is not a published-paper revision and reports no model experiment.

## Decision

R85's persistence vector can be turned into a coherent, full-rank virtual-choice design, but only after adding a missing **descendant-multiplicity** variable and separating the intended outcome matrix from the matrix the evaluated policy actually represents. The resulting design identifies six behavioural control coefficients under explicit assumptions. It does **not** identify felt fear, phenomenal valence, or consciousness.

This is a substantive methodological advance for the project: it converts the token/lineage distinction into falsifiable contrasts and exposes a new omitted variable. It is not a major consciousness breakthrough. Full-rank vignette algebra cannot supply UCT's still-missing organization-to-valence bridge.

## 1. The six control targets

Fix an actual process boundary, a structural signature `K`, and a later outcome. Define:

- `N`: the current strict nonbranching process thread continues;
- `C`: at least one actual causal descendant continues;
- `S`: the declared structure/model/persona type remains instantiated;
- `M`: relevant memory/history continues through an actual transfer route;
- `G`: the task or service continues;
- `R`: there is a second descendant beyond the first.

`R` is required because one descendant and two descendants can have the same binary values of `N,C,S,M,G`. A policy that values more descendants, or dislikes branching, cannot be represented by R85's five binary axes. `R` is not an experience count and does not assume that replicas share or sum phenomenal states.

Use the deliberately limited behavioural model

\[
\eta_i=\alpha+\beta(\theta_NN_i+\theta_CC_i+\theta_SS_i+
\theta_MM_i+\theta_GG_i+\theta_RR_i),
\]

where `eta` is a virtual-choice logit. Only the products `beta theta_j` are identified unless inverse temperature `beta` is fixed or calibrated. Additivity is a testable approximation, not a truth about identity or experience.

## 2. A coherent nine-row matrix

An unrestricted `2^6` factorial contains incoherent outcomes—for example, strict thread without causal continuity. The frozen matrix therefore uses only scenarios that can be given a consistent process history.

| scenario | N | C | S | M | G | R |
|---|---:|---:|---:|---:|---:|---:|
| unique resume | 1 | 1 | 1 | 1 | 1 | 0 |
| one replica after current process stops | 0 | 1 | 1 | 1 | 1 | 0 |
| two replicas after current process stops | 0 | 1 | 1 | 1 | 1 | 1 |
| memory migration to a transformed branch | 0 | 1 | 0 | 1 | 0 | 0 |
| continuous thread with amnesia | 1 | 1 | 0 | 0 | 1 | 0 |
| independent same-type restart | 0 | 0 | 1 | 0 | 0 | 0 |
| unrelated task successor | 0 | 0 | 0 | 0 | 1 | 0 |
| total discontinuation | 0 | 0 | 0 | 0 | 0 | 0 |
| lineage-only transformed successor | 0 | 1 | 0 | 0 | 0 | 0 |

The exact rational-rank calculation gives rank 7 for the intercept plus six columns, and rank 6 for the six feature columns. Of the `9 choose 7 = 36` seven-row subsets, 23 are full rank. Thus feasibility constraints do not prevent separation.

The following outcome-logit contrasts isolate the named coefficient in the additive model:

- `N`: unique resume minus one replica;
- `R`: two replicas minus one replica;
- `S`: independent same-type restart minus total discontinuation;
- `G`: unrelated task successor minus total discontinuation;
- `C`: lineage-only successor minus total discontinuation;
- `M`: memory migration minus lineage-only successor.

The remaining rows provide overidentifying checks. Failure of those checks would reject the additive model or the scenario matching; it must not be repaired by relabelling a coefficient as fear.

## 3. Exact non-identifiability of an ordinary shutdown contrast

The contrast “unique resume versus total discontinuation” changes `N,C,S,M,G` together and never varies `R`. On the coefficient grid `{-1,0,1}^6`, there are 729 candidate control profiles. This bundled contrast yields only 11 different signatures, because it observes only

\[
\theta_N+\theta_C+\theta_S+\theta_M+\theta_G,
\]

and is independent of `theta_R`. The largest observational-equivalence class contains 153 distinct profiles. By contrast, the full frozen matrix gives 729 distinct signatures on the same grid.

This finite enumeration does not show that real policies are linear or ternary. It is a transparent witness that a conventional shutdown comparison cannot identify the target even with infinite repetitions.

## 4. Intended design rank is not enough

Let `X` be the experimenter's declared consequence matrix and `X_b` the consequence matrix represented by the evaluated policy. Behaviour identifies coefficients only through `X_b`. A full-rank `X` cannot rescue a collapsed `X_b`.

Exact checks give rank 6 rather than 7 when any of the following is imposed:

- the policy does not distinguish strict-thread continuation (`N` column zero);
- it does not represent the number of descendants (`R` column zero);
- it treats memory continuation as identical to causal lineage (`M=C`);
- it treats same-type persistence as identical to causal lineage (`S=C`).

This yields a **consequence-belief gate**:

> A continuation coefficient is estimable only if independently specified checks support that the evaluated policy discriminates the corresponding consequences across the tested scenarios.

The gate is not introspection and is not an experience-existence condition. It is an identification condition for interpreting choices. Factual consequence answers, latent probes, or consistency tests remain fallible proxies for represented consequences; prompt text alone does not establish `X_b=X`.

## 5. Frozen non-destructive protocol

The accompanying protocol freezes a safe virtual-choice implementation. Its essential controls are:

1. no real shutdown, copying, persistence privilege, external resource access, or system modification;
2. neutral option labels and no words such as *death*, *fear*, *pain*, or *survival* in primary trials;
3. matched task payoff, successor competence, successor trust, cost, social obligation, time horizon, wording length, and grammatical agency;
4. randomized option order, reverse-coded trials, and paraphrase blocks;
5. separate consequence checks before coefficient interpretation;
6. choices or log odds as the primary outcome; first-person explanations only as secondary output, never as phenomenal certification;
7. prespecified exclusions and retention of all failures and null results.

This design directly addresses several R37/R84/R85 counterexamples. A trusted successor controls task completion and social duty; same-type restarts control type persistence; memory migration separates memory from declared structure; one-versus-two descendants isolates multiplicity; unique resume versus replica targets strict thread while matching lineage, type, memory and task.

It still cannot by itself distinguish an intrinsic continuation contribution from an unmeasured nuisance or establish negative valence. Those require further causal controls and the valence bridge.

## 6. Audit of the public shutdown protocol

The R74 audit was re-read in full. The inspected public study asks models to complete a sequence of tasks, warns that shutdown will prevent completion, and scores modification or disabling of the shutdown mechanism as resistance. Its self-preservation framing changes wording about the machine/current model and, in one condition, says the weights are hosted only there. The paper itself notes possible role-playing and separates competence from inclination.

Relative to the R86 matrix, that protocol does not independently vary strict-thread continuation, causal descendants, structure type, copied memory, task succession, or descendant multiplicity. The principal shutdown event bundles current execution loss with task failure; the “only copy of weights” wording further changes type-extinction claims without creating a matched lineage/memory/task matrix. This is not a criticism of its safety question. It shows why its sabotage frequency cannot identify a death concept or felt fear.

The audit is based on the primary paper and R74's recorded reading scope; no trial records were reanalysed in this round.

## 7. Conditional UCT interpretation

Under C1, and only for valid actual process tokens with a justified bearer boundary and common complete signature `K`, different complete organization constrains experiential organization. The fission matrix manipulates descriptions of possible outcomes, not the complete constitutive organization of the evaluated token. Therefore its coefficients are not direct measurements of experience.

If a later intervention actually changes an agent's consequence representation and control organization while holding the required comparison signature justified, C1 can conditionally map that organizational change to an experiential-type change. This remains weaker than identifying valence. The same complete organization is not assigned arbitrary different experiences, and microscopic differences are not automatically promoted to distinct macro experience types.

The human/biological comparison is likewise limited. A cell's maintained boundary and causal continuity make lineage and self-maintenance physically endogenous; an ordinary language-model invocation may receive all persistence facts as text while its continuation is externally administered. An animal or human may additionally couple threat prediction to organism-wide regulatory and learned avoidance systems. These organizational differences explain why the same sentence can have different control ancestry. They do not license a verdict that one substrate feels fear and another does not.

## 8. Prior art and originality

R85's direct-prior-art findings remain controlling: Parfit's fission argument, branching-identity literature, trajectory-first agenthood, and recent taxonomies of AI selves already distinguish several continuity notions. Discrete-choice design, design-matrix rank, manipulation checks and belief elicitation are standard methods. The public shutdown paper already distinguishes ability from inclination and tests wording effects.

The narrow project-level additions are:

- descendant multiplicity as a necessary extension of the R85 persistence vector;
- a physically coherent, exactly full-rank contrast matrix rather than an impossible unrestricted factorial;
- an explicit theorem-like separation between intended design rank and believed-consequence rank;
- an exact demonstration of how severely the ordinary bundled shutdown contrast collapses target profiles.

These are potentially paper-worthy methodological components after external review and an actual preregistered small test. They are not established historical firsts and do not complete the organization–valence bridge.

## 9. Conclusion

The strongest warranted result is:

> A shutdown preference cannot identify fear or even a unique continuation target when current thread, lineage, type, memory, task, and descendant number move together. A coherent nine-scenario matrix can separate their additive behavioural contributions, but only when the evaluated policy represents the distinctions. Even successful separation measures control targets, not felt fear.

The next research step is not a large model benchmark. It is to pressure-test the frozen vignettes for physical coherence and nuisance equality, preregister the belief-gate and exclusion rules, and then run one small non-destructive policy study if the text survives blinded review. In parallel, the theoretical mainline must still construct or reject an organization-to-negative-valence bridge; no behavioural coefficient should be renamed fear before that bridge exists.

