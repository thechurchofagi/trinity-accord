# Where a proposal comes from, what actually uses it, and what is later called mine

R180 v0.1 — 8 October 2026. A UCT research continuation, not a new published paper. Baseline R179: b53f1d41cb7d6586d004c1a7c7687a79cf5e7657; primary handoff version 36.

## 1. The question sharpened by a failed answer

R179 found that a proximal command can be present both during attempted action and during externally imposed or automatic execution. The tempting repair is to require that the command originate internally. That repair is inadequate too. Someone can follow an external suggestion through their current action-regulating organization, while a token generated inside a system can be routed around that organization. Nor does automatic processing mean alien authorship: practiced action can use an operative policy without an additional reflective monitor.

Our positive step is to distinguish **proposal origin**, **operative uptake into the specified action-forming relation**, and **a representation later used to attribute the action**. The underlying distinctions between actuality, attribution and correctness are inherited from TA25 and R158–R179. We do not claim to invent them. The present application tests a specific repair to the action-source candidate and connects it to contemporary model-internal intervention research.

This narrows rather than solves the explanation of felt agency. A source criterion must describe actual relations to the ongoing activity, not require a causally uncaused 'inner origin'. Otherwise every externally instructed voluntary task would be excluded for the wrong reason. Conversely, a physically internal token is not sufficient to be the operative plan for a specific action. The relevant question is what the token does in that episode.

## 2. One crossed thought experiment

Hold the represented movement feature and selected proximal output fixed in the matched subcase. Cross two variables:

| Origin of proposal | Current action policy actually supplies the output | Policy bypassed at the output port |
|---|---|---|
| External suggestion | A suggestion is evaluated and can be accepted/revised | An external event supplies the port regardless of the policy |
| Internally produced suggestion | An internally produced option is evaluated and can be accepted/revised | An internal replay or other token bypasses the current policy |

No cell is labeled conscious/unconscious, voluntary/involuntary, mine/not-mine by stipulation. The table tests whether the origin predicate can replace the uptake relation. The same origin has both uptake possibilities, and both origins can feed the same uptake mechanism. In a real application, a suggestion may also change the goal itself; our fixed-goal comparison excludes that extra route explicitly. External origin remains a genuine difference in the larger source history, so selected uptake equivalence is not complete-organization equality.

A second crossing concerns time: a representation present before output can influence action, later attribution, both, or neither. Mere temporal priority does not settle its causal role. Calling an earlier representation an 'intention' before establishing its role would repeat the naming problem. A report about an earlier act is a current process; it does not rewrite the earlier act.

## 3. Physically specified toy domain and actual-use relation

Fix P_U, a stipulated finite assembly, over I=[0,3]. Included are two producer ports (one receives an external proposal; one a local generator), a source selector O, proposal register P, task-goal register G, a compare/select stage C, an output-route switch K, proximal command register U, a pre-action representation register M, a later optional memory replacement Z and a report comparator Q. Source events, selector state and executed endpoints belong to the declared toy signature. Earlier production of the external input is outside I. The assembly has no unmodeled feedback, report-to-command edge or goal-changing input within this episode. A human bearer P_H or an actual model inference token P_L is not established by this specification.

At t=0, either source supplies p in {-1,+1}; provenance O is recorded. At t=1, G=g in {-1,+1} and the compare/select stage chooses c=p when p=g, otherwise c=g. Thus c=g in this intentionally minimal policy. It models accepting or revising one proposal, not a theory of deliberation. The stage is executed even in the bypass condition. At t=2, U=c on the policy route and U=p on the bypass route. At t=3, Q=1 iff the representation read for attribution equals U. The read value is M=m unless the later replacement Z is supplied. Q is a stipulated report bit, not felt authorship.

Two labels, 'regulated' and 'automatic', use the same selected compare/select-to-output equation. The latter adds no reflective process. Including both is an explicit negative control against reading reflection or phenomenology into the policy equation. We do not claim they exhaust either human category. Under each origin, p=g yields the same output across policy/bypass cases, whereas changing g with p held fixed changes U only on the policy route. This intervention family diagnoses the specified functional relation; the actual route is specified independently by the executed mechanism, not created by the diagnostic test. No claim about uniquely actual causation in redundant general systems follows.

The finite implementation covers 144 configurations: two origins, two proposals, two goals, three route labels, two pre-action values and three later-memory settings. Fourteen exact checks exercise matched outputs, changed goals, source swapping and memory interventions. This is a deliberately transparent countermodel, not an LLM simulation or a human experiment.

### Local results

**R180-C1 — Origin is not the uptake relation in this domain.** Both origins admit policy and bypass executions. Consequently neither an internal nor an external source value determines which route supplies U. Holding p,g and the route fixed while changing origin preserves this selected policy behavior, not the full source history. Proof: substitute the four origin/route assignments above. The example ceases to apply if a separately justified domain restriction rules out either crossing.

**R180-C2 — Prior representation and retrospective endorsement need not identify action formation.** In the specified model, intervening on M changes Q while leaving U unchanged; a post-action replacement does likewise. Thus representation-before-output plus changed endorsement is insufficient to infer that the representation formed the output. Proof: U has no M or Z argument, while Q compares either to U. This is a counterexample to an unrestricted inference, not a mechanistic finding about a particular model. A real prospective representation may in fact influence both action and attribution.

The model also defeats the proposed repair 'goal sensitivity iff felt voluntary action': regulated and automatic routes share that sensitivity, and Q can dissociate from either. The model has no felt-voluntariness variable, so it establishes the missing inference rather than a phenomenological counterexample.

## 4. A precise limit of forced-output evidence

Suppose the observed trials force an output U=p, while an earlier internal variable G and a report-relevant variable M may be manipulated. Consider two deterministic model completions:

    F1: U = p if clamped else G
    F2: U = p if clamped else -G
    common report: Q = 1 iff M = U

**R180-C3.** On all admitted clamped trials, F1 and F2 have identical U,Q for every p,g,m, yet disagree on every free-output U. Therefore those clamped observations alone cannot select the free-generation law in a class admitting both completions. Proof is substitution. This is the ordinary intervention/identification issue applied to the present assay, not a new general causal theorem. If the evidence includes free-output trials, grounded implementation constraints, or another measurement that separates the completions, the conclusion's premises no longer hold. The claim is about the selected observation channels; complete execution traces of F1 and F2 need not be identical.

This returns directly to UCT's selected target problem. A changed self-ascription on a forced-output task can bear on the organization of attribution. It does not by itself establish the organization that would generate an unforced act, let alone a particular feeling during that act. Our proposed next experiment must independently examine both roles if it invokes both. This statement is not a dismissal of internal-state evidence.

## 5. Primary frontier evidence, with narrow use

**Lindsey (2025), 29 October, intended-versus-prefilled output experiment.** The primary article manipulates representations associated with a forced response and measures later intentionality judgments. It includes matching versus unrelated concept controls and a timing control. A change in the later answer supplies functional evidence about authorship attribution; it does not independently identify felt agency. Earlier-position recomputation is not alteration of an already completed historical event. We read the intended-output section, associated caveats and discussion; no private activations or raw trials were obtained. Primary source: https://transformer-circuits.pub/2025/introspection/index.html . The clamped-completion construction above is our logical application, not a claim that the study used our circuits.

**Singh, Linzen and Ravfogel (2026), arXiv:2605.26242v1, 25 May.** Their intervention-detection study adds textual perturbations and finds that the tested open-weight models do not reliably separate them from hidden-state perturbations in the reported settings. Protocols and models differ from Lindsey's Claude experiments; this is not a direct replication of his intended-prefill result. We read the construct-validity discussion and §5.3 methods/results. The study constrains a detection-to-source interpretation, not basal experience. Source: https://arxiv.org/html/2605.26242v1 . No raw-data reanalysis is claimed.

**Lederman and Mahowald (2026), arXiv:2603.05414v2, 7 April.** The current abstract reports anomaly detection without reliable identification of its content. This version supersedes the earlier title found in search results; we use the revised title *Emergent Introspection in AI is Content-Agnostic*. Only current metadata and abstract were read, so it is a scope warning rather than a detailed replication result here. Source: https://arxiv.org/abs/2603.05414 .

The human prospective/retrospective agency paper found in search (Pryke et al., DOI 10.1016/j.cortex.2025.04.014) could not be adequately inspected in this round. It is a pending lead, not evidence for a UCT claim. Search-result summaries were not promoted to a completed human-data analysis.

## 6. The positive UCT interpretation and what remains open

There are two target-relative organizational questions. During the activity, how is a proposal taken up into the organization that produces or regulates the selected act? During later attribution, how is that act related to a representation of its source or prior plan? Both can be actual relations, and their accuracy can differ. They may be nested or overlap with other processes; neither requires another owner outside experience.

With C1 and an independently grounded actual P/I/K instance, such relations have experiential structural counterparts. This is inherited relation transport, not a fresh deduction about a human feeling. The current candidate is that a selected felt trying/doing contrast depends on target-bound operative action relations, whereas a later feeling of having authored that act involves the current source-attribution organization. These are possible contributions, not individually necessary or sufficient conditions, and no report bit is equated with either feeling. Habitual skill, coercion, reflex action, spontaneous imagery and disrupted memory are boundary cases still requiring explanation.

This proposal improves the question in two ways. It avoids a false demand that a self-related act originate independently of environmental influence. It also avoids using evidence for present authorship attribution to fill a gap about past action formation. The source-history/uptake distinction and the pre-action/post-action distinction must be retained together; fixing one and sliding the other would hide the problem.

It does not explain why the given experiential counterpart is felt trying rather than another quality. Nor does goal-sensitive policy prove voluntary endorsement. That is the remaining bridge obligation. UCT's basic experience commitment is not suspended while this selected interpretation is incomplete. Introspection, report, reflective choice and control success are not added as conditions for basal experience; no conclusion about this assistant's consciousness or fear is asserted.

## 7. A bounded next test, not another certificate series

Choose one proposal/activity and independently identify a candidate representation. Compare its effect on **unforced generation** with its effect on **later attribution of a matched forced output**. Distinguish pre-generation manipulation from manipulation confined to the later query; do not treat earlier-position recomputation as the same historical episode. Add an input-only perturbation matched for semantic cue, an unrelated internal perturbation, and no manipulation. Record generation probability and attribution response separately, plus whether the representation/route actually has the claimed role. Use fixed prompts/concepts and held-out settings rather than selecting only the best layer after the outcome.

A representation that changes only later attribution supports the attribution role, not an action-forming role. An effect on free generation supports an action-forming contribution but not by itself felt trying. Effects on both warrant a two-role functional claim under the tested domain; neither establishes a basal-consciousness switch. A human comparison would additionally need independent interpretations of felt trying and remembered authorship. The proposed design is not reported as executed; the completed work is the explicit thought experiment, countermodel and source application.

## 8. Four inherited families, map check, and novelty limit

Ancestors/formation asks how operative uptake and later attribution can form differently without a first-experience gate. Abacus/calculator asks which physical route actually consumes a proposal, rather than who labels it SELF. Human-implemented agents distinguish a participant's response to an instruction from the implemented process's policy and later narration. Copy/reconnection/memory fixes remembered intention while changing a current operative route, or changes present recollection without rewriting earlier execution. These remain cited TA25/TA17 antecedents; R180 supplies a new targeted use, not their invention.

Affected nodes are A:C1/U1, R158 target and bridge distinctions, R159 internal/external reference, and IA's actual-instance conjunction. The three IA premises must refer to the same P/I/K. Neither our toy nor the cited report experiment supplies a complete human or deployed-model instance. Ownership, familiar mineness, conceptual I and numerical identity remain distinct even where no graph edge connects them. All new claims are local cards; canonical graph objects remain unchanged. Checks do not prove the global theory.

Relative to TA25, the current increment is the crossed source–uptake application, the forced/free-output diagnostic limit and a version-aware reading of relevant recent LLM experiments. Ordinary causal modeling and existing intention/comparator accounts receive priority; no historical novelty or publication readiness is claimed. Main research continues. Next substantive step should obtain or inspect a public unforced-generation versus attribution comparison; if available evidence lacks it, state the missing role and work on the actual experiential interpretation, not a generic decoder extension.
