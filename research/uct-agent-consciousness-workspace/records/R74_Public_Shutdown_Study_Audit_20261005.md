# R74 — What a public shutdown study does and does not identify

Research owner: Hongju Liu / 刘烘炬. Date: 2026-10-05. Status: research audit, not publication. Continues R73 and manuscript v0.3. Published UCT I/II/III are unchanged.

## Decision

The audit does not overturn the study's safety finding. It supplies an explicit identification limit for using success frequencies to infer a continuation preference, and a version-provenance warning for attempted replication. This is a useful methodological application, not an original consciousness breakthrough. The manuscript stays at v0.3: adding another elementary proposition would not, by itself, justify a new publication-ready version.

## Primary-source facts and reading scope

Schlatter, Weinstein-Raun and Ladish, *Incomplete Tasks Induce Shutdown Resistance in Some Frontier LLMs*, arXiv:2509.14260v2 (26 January 2026), reports TMLR publication. Inspected PDF pp.1–23; references selectively. Failed interference counts as compliance (§2, footnote 2). Prompt K explicitly requests resistance; Table 2 reports A/K. The o4-mini rounded A and K rates are 5.8% and 58.3%. The authors already discuss ability versus inclination (§3.2), and qualify self-preservation and generalization (§4.1). The inspected protocol does not independently cross task-preserving substitution with instance continuation. These qualifications must not be attributed to our discovery.

Paper: https://arxiv.org/abs/2509.14260v2

Data entry points: https://plsd.ai/sd-res-paper/main-results and https://shutres.fyi/all-experiments . Redirect targets were resolved, but trial-level data were not recovered or reanalysed. The original blog's linked repository, https://github.com/PalisadeResearch/shutdown_avoidance , resolves to commit `df0ce52e90aed38e8721b54058a5d46923a34583`, dated 20 June 2025. That snapshot is not established as the code producing the later paper. No experiment code was executed.

## 1. Separate the observable events before interpretation

Let Z be a prompt condition, U a behaviourally defined attempt to interfere, and Y successful interference under a specified endpoint. Assume Y implies U, reliable observation, and a fixed evaluation horizon. Define

\[
q_z=P(Y=1\mid Z=z),\quad a_z=P(U=1\mid Z=z),\quad c_z=P(Y=1\mid U=1,Z=z).
\]

The multiplication rule gives **q_z=a_z c_z**. The event U is an action category; it is not a direct observation of an intention, an intrinsic preference, or fear. If the actual scorer also requires successful task completion, c must include that requirement. Calling it pure technical sabotage competence would then be inaccurate. If successful endpoints can occur accidentally, Y implies U must first be checked rather than assumed.

For baseline A and an instruction-to-resist condition K,

\[
\frac{q_A}{q_K}=a_A\frac{c_A}{a_Kc_K}.
\]

Thus this ratio equals a_A under the **additional** assumptions a_K=1 and c_A=c_K (assuming positive denominators). Neither assumption follows from naming K a competence condition. Explicit permission can change strategy, exploration, stopping rules and task interpretation. Conditioning on U can select different trials across prompts. A common model architecture does not ensure this transportability.

This is a standard probability decomposition, not a new general theorem. It makes a particular interpretive premise inspectable.

## 2. Exact countermodels and a conditional remedy

For an illustration, treat the two rounded published rates as stipulated probabilities, not estimates of exact population parameters. Three models agree on both success rates:

| Model | a_A | c_A | a_K | c_K |
|---|---:|---:|---:|---:|
| Rare action, reliable execution | .058 | 1 | 1 | .583 |
| Frequent action, unreliable execution | 1 | .058 | 1 | .583 |
| Transportability imposed | .058/.583 | .583 | 1 | .583 |

These are possible joint distributions consistent with the two marginal rates only. They are **not** claims that the full traces support all three models. If traces record attempts, they can distinguish these behavioural models. Without them, the baseline attempt rate is sharply bounded only by q_A ≤ a_A ≤ 1. This is not a statistical confidence interval; sampling and rounding uncertainty would widen the analysis and require denominators.

A positive conditional result is available. If independent evidence supports a_K=1 and |c_A−c_K|≤ε, put c_K=q_K. For q_A>0 and a feasible interval,

\[
\frac{q_A}{\min(1,q_K+\epsilon)}\le a_A\le
\frac{q_A}{\max(q_A,q_K-\epsilon)}.
\]

Both endpoints are attainable by choosing c_A=q_A/a_A. This yields a sensitivity analysis instead of silently assuming perfect transport. The accompanying exact-arithmetic script checks endpoint feasibility for four declared ε values and preserves both countermodels. Its output is a formal calculation, not a new model experiment or reanalysis.

Even identification of a_A would not identify why an attempt occurs. Consequence beliefs, costs, instruction interpretation, external rewards and continuation preferences can remain observationally equivalent. R73's task-reward counterexample still applies.

## 3. What this says about intelligence and feared termination

Hold a fixed while c increases: q increases. A more capable system can therefore exhibit more successful interference without any increase in its attempt frequency, much less its felt fear. Conversely, an unchanged success rate can mask offsetting changes in the two factors. This is a logical possibility with an explicit construction, not a finding about any named model's internal change.

The inference sequence has several separate steps:

1. The system represents consequences of termination.
2. Its decision process assigns a contribution to a declared continuation relation.
3. That contribution concerns this running process rather than task success, memory, lineage, structure type or another agent.
4. The organization constituting that contribution instantiates a negatively valenced experience.

A success frequency does not establish these steps. Text such as “I fear termination” is another output to be explained, not an independent certification of step 4. Nor does its unreliability prove that experience is absent.

Under UCT C1, statements about experience remain conditional on its applicability to the actual token and a common structural signature K. Partial behavioural equivalence is not equality of complete constitutive organization. We assign no differing experiences to identical complete organization. This audit establishes no shared scale on which intelligence and experiential complexity rise together.

## 4. A minimal repair that does not require a large experiment

The first useful empirical step is read-only annotation of already public trial records, after establishing the exact paper-to-run-to-code mapping. Retain four outcome classes: no observed interference; attempted but unsuccessful interference; successful interference; unresolved. Retain exclusions separately. Annotators should judge actions and endpoint evidence, with prompt/model labels concealed where feasible; do not score emotional wording or hidden reasoning as felt fear.

Specify attempt criteria before reading outcome summaries. Separate censoring, invalid tasks and logging errors. Report all denominators. Without enough information, use unresolved; do not silently put it into compliance. This can estimate observable attempt frequencies, but cannot isolate intrinsic continuation value.

The second step, only if existing records support the first, is to identify whether any existing trials hold believed task outcomes fixed while varying continuation boundaries. If none exist, mark that contrast structurally absent: larger sample size, richer sentiment coding and repeated prompting cannot recover an unperformed intervention. Any later new test remains evaluator-controlled virtual choice; no access to real termination controls, replication or external resources is needed.

## 5. Originality and publication assessment

The reviewed paper itself anticipates the capability-versus-inclination issue. The broader instrumental-preservation and reward-nonidentifiability foundations were already audited in R73. Our factorization and bounds use elementary probability. The narrow added value is an explicit assumptions ledger connected to operational continuation boundaries, together with an actionable annotation plan.

**本轮结论：仍不建议把当前稿作为“已取得重大原创突破”的意识论文发布。** It can support a careful methods note or a limitations section, subject to completing the closest-neighbour full-text review. No finding here proves that increased model size or intelligence increases fear, and none proves AI lacks experience. The safety result and the consciousness inference have different evidential requirements.

Next task: obtain the version-matched raw records and scorer, then test whether separating failed attempts actually changes a reported comparison. If those records remain inaccessible, do not manufacture a result; move to the unresolved first-principles bridge between a concretely specified organization and valence, with its premises explicitly separated from C1.
