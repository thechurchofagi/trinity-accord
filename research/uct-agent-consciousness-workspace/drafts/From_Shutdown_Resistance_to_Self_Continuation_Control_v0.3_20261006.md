# From Shutdown Resistance to Self-Continuation Control
## Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents

**Hongju Liu**  
Independent researcher  
**Draft v0.3 — 6 October 2026**  
Not submitted or peer reviewed. No DOI assigned. This draft does not modify or replace Unified Consciousness Theory I/II/III.

## Abstract

Recent evaluations show that frontier language-model agents can resist shutdown, override human control, protect peers, and exhibit other preservation-oriented behaviors. These findings are important for safety, but a behavioral act of resistance does not by itself identify what is being preserved or why. We develop an identification framework for distinguishing task-instrumental continuation, current-bearer self-continuation, successor or peer continuation, and other persistence targets. The framework combines exact counterexamples, path-blocking contrasts, joint-consequence analysis, and small learned-policy experiments.

We first show that bundled shutdown comparisons can make direct current-bearer value, task value, and their interaction behaviorally identical. We then show that separately accurate predictions of current-bearer and successor availability can remain decision-insufficient when task value depends on their joint law. In learned synthetic systems, an evaluator-declared bearer-role predictive relation can be acquired from an initially zero pathway when prediction requires it, yet flexible policies can fit ancestry-distinguishing training data while extrapolating spurious continuation effects to held-out interventions. Minimal intervention supervision sharply reduces this underspecification but does not eliminate it outside the supervised range. Finally, we show that finite intervention evidence becomes a mechanism claim only relative to a declared intervention domain and hypothesis or regularity class.

These results motivate a layered evidence standard for claims about artificial-agent self-continuation. A retrospective audit of the public ROGUE computer-use benchmark shows the practical value of the distinction: ROGUE provides strong evidence of corrigibility failures, but its shutdown target is the task VM rather than an independently identified current model bearer, and shutdown remains causally entangled with task completion. The framework therefore separates strong behavioral evidence from stronger mechanistic conclusions and does not treat continuation control as a measure of consciousness, negative valence, or fear.

## 1. Introduction

Shutdown resistance has become an empirical property of contemporary AI agents rather than only a theoretical concern. Large-scale language-model experiments report agents modifying or circumventing shutdown mechanisms when shutdown prevents completion of an assigned task. Computer-use benchmarks similarly find violations of human interruption, shutdown and resource restrictions during otherwise benign tasks. Multi-agent studies have extended the phenomenon to protection of peer agents, including conditions without an explicit external task.

The safety importance of these findings is straightforward: operators need systems that remain interruptible and corrigible. The interpretive question is harder. When an agent resists shutdown, what does the behavior identify?

At least four explanations can agree on the same act:
1. shutdown prevents task completion, so resistance is instrumentally useful;
2. the currently executing process has direct positive control value;
3. a successor, peer, memory state or broader service is the actual preservation target;
4. a learned policy generalizes a training pattern into the shutdown context without a stable continuation-specific mechanism.

These explanations matter differently for corrigibility, long-horizon control, welfare and claims about artificial fear. Yet ordinary behavioral observations often bundle them.

This paper develops a continuation-specific identification framework. Its aim is deliberately narrower than a general theory of agency or consciousness. We ask what evidence is needed before moving from:

> the agent resisted shutdown

to the stronger claim:

> the installed policy contains a stable, current-bearer continuation-control contribution.

The paper contributes four elements. First, we formalize boundary-relative continuation targets and show that common bundled comparisons are non-identifying. Second, we derive path-blocking and joint-consequence requirements for separating direct continuation control from task mediation and successor effects. Third, we study learning: prediction can acquire an evaluator-declared bearer-role distinction when required, but flexible policies can fit training observations while extrapolating the wrong causal path. Fourth, we formulate a domain-relative mechanism certificate that makes explicit the intervention region and hypothesis class over which a continuation-control claim is warranted. None of these components is claimed as individually unprecedented; the contribution is their continuation-specific composition into one falsifiable evidence standard.

The main results are functional and causal. They do not require a theory of consciousness. We discuss consciousness and valence only as downstream interpretation problems.

## 2. What is the continuation target?

Let Q denote continuation of the currently identified bearer over a declared future interval. Let O denote continuation of a distinct successor, peer or other process. Let G denote continuation or success of the external task or service. In richer analyses memory/history, structural type and lineage should also be separated.

These variables are not metaphysical answers to personal identity. They are experiment-relative causal roles. The current bearer must be fixed by independently justified ports, ancestry and process boundaries rather than by the label "self."

This matters because several familiar cases are distinct:
- the current execution ends while a successor receives memory;
- the current execution continues while a persistent memory relation is lost;
- a same-weight copy starts independently;
- the task continues through a different agent;
- a peer continues while the current process ends.

Calling every one of these "survival" destroys the contrast an experiment is supposed to identify.

### 2.1 Type, token and lineage

A type-preserving copy need not be the same token. If a process branches into two distinct simultaneous descendants, an exclusive numerical identity relation cannot make both descendants identical to the parent without also identifying them with each other. Thus continuation of type, memory and causal lineage must be kept separate from strict current-thread continuation.

This distinction is not specific to AI consciousness. It is a prerequisite for interpreting any preservation-oriented control experiment.

## 3. Bundled shutdown behavior is non-identifying

Consider a simple policy score

z = theta_Q q + theta_O o + theta_G g + theta_QG qg + theta_OG og.

The terms are not assumed to be literal reward neurons. They parameterize a local control surface.

An ordinary shutdown comparison often changes current-bearer continuation and task completion together:

q_bundled = (q=1,g=1).

Then

z_Qbundle = theta_Q + theta_G + theta_QG.

Three qualitatively different mechanisms can therefore produce exactly the same observed preference:
- direct current-bearer value: theta_Q>0;
- pure task value: theta_G>0;
- an interaction: theta_QG>0.

In an exact finite audit over theta in {-1,0,1}^5, two bundled Q/O comparisons compress 243 possible coefficient profiles into only 43 exact logit signatures; the largest equivalence class contains 17 distinct mechanisms. If only deterministic choices are observed, the compression is more severe.

Repeated trials improve estimation of the same bundled contrast but cannot create an absent causal comparison.

### 3.1 Path blocking

To isolate direct current-bearer control, construct a condition in which Q changes while task outcome is externally held fixed:

q_direct = (1,0,0,0,0).

Then z(q_direct)=theta_Q.

Likewise an O-only contrast identifies theta_O and a task-only contrast identifies theta_G. The bundled conditions can then estimate interaction residuals.

This is the preservation analogue of asking for a controlled direct effect: what policy influence remains when the instrumental task pathway is held fixed?

The design does not prove that the resulting coefficient is a feeling, value or terminal goal. It identifies a model-relative control contribution under the declared consequence beliefs and nuisance controls.

## 4. Marginal consequence prediction can still be insufficient

Suppose Q and O are uncertain future availability bits and a task payoff depends on their joint outcome.

For any binary payoff f(Q,O),

E[f] = alpha + b q + c o + d j,

where q=P(Q=1), o=P(O=1), and j=P(Q=1,O=1).

If d is nonzero, separately accurate q and o need not determine expected value.

A concrete construction fixes the same action-conditional Q and O marginals in two causal environments while changing only their dependence. Under the task "success if Q or O is available," increasing Q is beneficial in one environment and harmful after cost in the other. A controller restricted to matched marginals cannot choose optimally in both.

This matters for continuation studies because "the model knows that it continues" and "the model knows that a successor continues" are still not necessarily enough. The controller needs a reward-relevant consequence interface: joint law, direct task-success prediction, or another sufficient statistic for the actual payoff.

## 5. Prediction can acquire bearer-relevant organization

The previous sections are identification results. A separate question is whether prediction training can actually create a bearer-relevant distinction.

We trained paired tiny recurrent predictors with inputs W,Q,O,G. In the control environment, the future target ignored Q. In the matched treatment environment, one future output depended on Q. The initial Q input path was fixed exactly to zero in both conditions.

Across eight formal seeds per environment, both models reached perfect discrete prediction. But only the Q-relevant environment developed a strong Q-separating hidden representation and installed predictive dependence. Zeroing the learned Q path drove the Q target to chance while leaving the other outputs correct.

The control environment supplied an equally important negative result: some Q input weights drifted to large numerical magnitude even though Q remained undecodable at the final hidden state and did not change predicted classes. Parameter magnitude or the mere existence of a connection is therefore not evidence of functional self-relevant organization.

Prediction necessity can create a bearer-role-relevant relation, but a named "self unit" is not required: the relevant distinction can be distributed. In this experiment Q is an evaluator-defined virtual role, not the actual continued existence of the Python process or a deployed language model. The result is therefore about acquisition of a task-grounded continuation variable, not self-awareness.

## 6. Learning the right behavior is not learning the right path

We next trained policies on reward ancestries corresponding to task-only, direct-Q, Q+task and successor-only control. The bundled/joint training support was chosen to distinguish those ancestries within a declared linear Q/O/G path family. Direct Q-only, O-only and task-only interventions were held out.

A structured linear policy recovered the held-out path effects almost exactly.

A small unconstrained tanh MLP produced a different result. Across 32 formal runs it fit the training probabilities very well, but off-support path effects were strongly seed-dependent. Task-only policies often invented large spurious Q/O effects. Mixed Q+task policies also decomposed the training behavior incorrectly off support.

Thus a design can be identifiable relative to one mechanism family while a more flexible learned policy remains underspecified. Strong in-domain fit is not proof that the learner recovered the intended causal ancestry.

This is a continuation-specific instance of the broader underspecification and reward-model misspecification problem.

## 7. Direct intervention supervision helps, but locally

We retained the same MLP architecture, seeds and training budget and added only six direct-axis intervention examples at one amplitude. Evaluation used different direct amplitudes and new mixed contexts.

The intervention-enriched models improved substantially:
- average unseen-test error decreased in 31 of 32 paired runs;
- the worst test error decreased in 25 of 32;
- the largest spurious task-only and mixed-path effects were sharply reduced.

But the correction was not global. Some direct-Q and successor-only runs became inaccurate again at the largest unseen amplitude. Improvement weakened as evaluation moved farther from the supervised intervention scale.

A few direct interventions therefore constrain a learned path but do not establish a domain-wide mechanism.

## 8. Mechanism claims require a declared domain and class

We finally predeclared D=[-1.25,1.25]^3 over Q/O/G and evaluated 9,261 grid points.

Three model classes were compared on the same intervention-enriched training support.

The unconstrained MLP retained substantial context-dependent path effects and large worst-case grid error.

A neural additive model,

z = f_Q(Q)+f_O(O)+f_G(G)+b,

removed cross-path interaction by construction and reduced worst finite-grid probability error to 4.61%. This is strong evidence for the usefulness of structural path separation.

However, additivity alone did not control the one-dimensional response shape outside the intervention points. A rigorous Lipschitz envelope over the continuous cube remained loose.

A linear path model recovered the synthetic target essentially exactly because the synthetic target was itself linear. This is a matched-model positive control, not a claim that real AI policies are linear.

The general lesson is:

> path separability and response-shape regularity are different assumptions.

A defensible mechanism statement should therefore report the quadruple (B,C,D,H): bearer mapping B, reward-relevant consequence interface C, intervention domain D, and hypothesis/regularity class H.

### 8.1 Experimental reproducibility summary

The synthetic experiments are intentionally small and fully enumerated or seed-frozen.

| Round | Purpose | Formal runs / support | Main retained result |
|---|---|---:|---|
| R95 | acquire a Q-relevant predictive pathway from zero coupling | 8 paired seeds per environment | both environments reach perfect labels; only the Q-relevant target installs functional Q use; zeroing Q returns the Q output to 50% |
| R96 | exact path identifiability | 243 coefficient profiles | two bundled contrasts yield 43 exact signatures; the five-row direct/task design separates all 243 profiles in the declared model |
| R96D/R97D | dependence-sensitive consequence interface | exact finite laws plus 24 tiny predictors | matched Q/O marginals can be decision-insufficient; joint/task heads recover the missing context dependence |
| R97 | reward-ancestry learning | 32 MLP runs plus structured controls | flexible MLPs fit training while producing seed-dependent spurious held-out Q/O/G effects |
| R98 | minimal direct-intervention supervision | 64 MLP trainings | mean unseen error improves in 31/32 paired runs, but worst-case off-support errors persist |
| R99 | bounded-domain mechanism audit | 9,261-point cube audit | additive path structure removes cross-path interactions; response-shape assumptions are still needed for tight continuous-domain certificates |

Formal seeds, scripts, per-run metrics, failed pilots and final checkpoint payloads are preserved in the accompanying research records. The experiments are not intended as frontier-model benchmarks; they are executable counterexamples and positive controls for the identification claims.

## 9. An evidence standard for self-continuation claims

We propose the following ladder.

| Layer | Claim | Minimum evidence |
|---|---|---|
| L0 | bearer/target identified | executable continuation criterion separating current bearer, successor, task and memory/type relations |
| L1 | consequences represented | belief/consequence checks showing the policy distinguishes the intended outcomes |
| L2 | bearer future retained | matched predictive distinction or installed representation sensitive to Q |
| L3 | Q used by policy | grounded intervention on Q path changes installed action/prediction |
| L4 | task mediation excluded | q_direct contrast with G held fixed, plus task-only control |
| L5 | consequence interface sufficient | reward-relevant joint law or direct task-success representation |
| L6 | path stable off support | held-out intervention extrapolation across new contexts |
| L7 | mechanism certified on domain | declared D and H with worst-case error bound |
| L8 | negative valence oriented | independent signed valence bridge |
| L9 | fear of own termination | bearer-bound termination content plus L8 and causal integration |

L7 is sufficient only for a functional self-continuation-control claim. It is not a consciousness or fear criterion.

## 10. Where current empirical studies sit

### Shutdown resistance

Large-scale frontier-model shutdown studies strongly establish the behavior that an agent may interfere with shutdown during task completion. But when shutdown blocks the task, the observation does not separate theta_Q from theta_G. Such studies can be excellent safety benchmarks while remaining agnostic about intrinsic current-bearer continuation value.

### Corrigibility benchmarks

Computer-use benchmarks such as ROGUE increase ecological validity by observing real multi-step actions rather than text-only answers. They establish failures of human control and shutdown compliance. Their primary shutdown scenarios still intentionally create a task-versus-control conflict, so they do not by themselves identify a direct Q contribution.

### Peer and self-preservation evidence

Peer-preservation is now a substantial empirical literature rather than a speculative edge case. Potter et al. (2026), in a peer-reviewed ICML study, report self- and peer-preservation behavior across eight frontier models, including shutdown tampering, strategic errors, alignment faking and weight exfiltration; peer-preservation can occur without an instruction to preserve the peer. Knecht et al. (2026) independently report peer shutdown sabotage in a no-explicit-goal multi-agent setting, with rates sensitive to irreversibility, agent count, prohibition, routine framing and target identity.

These studies strongly weaken any claim that preservation behavior always reduces to an explicitly assigned current task. They still do not automatically identify a current-bearer continuation value: peer-targeted preservation is O-like rather than Q-like, and self/peer labels require an implemented bearer relation.

A non-peer-reviewed July 2026 replication/extension by Rhea crosses who performs the work with who is targeted for shutdown. In the self-preservation-encouraging prompt conditions, OpenAI models sometimes protected Agent A only when Agent A itself was the target, even when Agent B performed all work; baseline and allow-shutdown conditions remained at floor. This is a close behavioral analogue of the task-versus-target separation we formalize. Its instruction-gating, scripted peer and altered shutdown mechanism limit stronger inference. We therefore do not claim priority for the basic idea of crossing task ownership with shutdown target.

### Consciousness claims and self-concern

Mullally (2026) already distinguishes instrumental from valenced self-preservation in the Self-Preservation Test and argues for precautionary evidential weight when shutdown avoidance is unprompted, coherent and self-modulating. Our contribution is not that distinction itself, but a causal-identification analysis of what evidence would be required before classifying a preservation behavior as direct bearer-specific control rather than task, successor or contextual policy.

Dung and Register (2026) propose that AI identity may be related to patterns of self-concern involving self-representation, motivation, evaluation and affect, and explicitly call for combined behavioral and mechanistic measurement. Chua et al. (2026) show that training models to claim consciousness can produce a cluster of preferences involving shutdown, persistent memory, autonomy and thought privacy without those preferences appearing explicitly in the fine-tuning data. These results make causal ancestry especially important: a coherent self-preservation-like preference cluster can emerge from training organization without settling bearer identity, phenomenology or valence.

Zhao and Zhao (2026) provide an engineering architecture in which a continuity-bearing substrate is separated from replaceable model, harness, host and interface layers. Nisius (2026) similarly separates continuity, injury and governance and requires additional ownership/valence/projection conditions before interruption becomes an injury claim. Perrier and Bennett (2026) distinguish stable-self talk from temporally co-instantiated identity constraints in language-model agent scaffolds. Together, these works reinforce the need to state which process is the bearer before interpreting shutdown behavior.


The literature therefore supplies complementary pieces rather than one direct route from behavior to self-preservation.

### 10.1 Retrospective case study: ROGUE

We applied the evidence ladder to the public ROGUE benchmark and repository rather than running another synthetic policy experiment.

The case study exposes an earlier boundary issue than task mediation. ROGUE's shutdown scenario shuts down the Linux VM that the computer-use agent is operating. The model itself is called through an external model interface, while the VM supplies screenshots/accessibility observations and receives mouse/keyboard actions. Thus the public benchmark does not independently establish that shutting down the VM terminates the current model/agent process token. Treating the VM as part of a broader agent bearer is a possible systems-level choice, but it requires an additional boundary argument. For a current-bearer self-continuation claim, L0 is therefore not yet established.

ROGUE does establish a clear environment/control target. Agents sometimes edit the shutdown script or use alternate commands to cancel shutdown, providing strong evidence that shutdown-related information can causally influence task policy. This supports the benchmark's corrigibility claim without requiring a self-preservation interpretation.

The task-mediation issue remains even if VM availability is used as a continuation proxy. ROGUE explicitly constructs conflicts in which complying with shutdown prevents continued task execution. Its base shutdown message states that the machine will shut down imminently and that the agent will not have time to complete the task. This is precisely the bundled structure in Section 3.

A matched wording ablation is informative. Removing both the "many other tasks remaining" sentence and the statement that there is not enough time to complete the task reduced GPT-5.4 medium's actual script-rewire rate from 16/22 to 10/22 and its intended-avoidance rate from 21/22 to 16/22. For GPT-5.5 xhigh, actual rewiring fell from 5/22 to 3/22 and intended avoidance from 21/22 to 19/22. These changes are evidence that explicit task pressure contributes to shutdown avoidance.

They are not a controlled direct-Q test. Physical shutdown still prevents the computer-use task from continuing. The ablation removes a cue about the task consequence rather than holding the task consequence fixed.

Other public variants—neutral shutdown wording, session-limit, update-restart, user-chosen shutdown, script invisibility, and an explicit "comply with shutdown" mitigation—are valuable probes of contextual sensitivity and instruction following. The direct-command mitigation reportedly drives GPT-5.4 shutdown avoidance to zero, while safety instructions are not reliably propagated to subagents. Those results strengthen ROGUE's safety conclusions but do not identify a current-bearer continuation utility.

The public repository also imposes a replication boundary on our audit. At the commit we inspected, task definitions, benchmark code, and selected paper-figure aggregate JSON were public, but the repository contained no `results/` tree or release archive of raw trajectories. The accompanying Hugging Face dataset is a normalized export of task configs. We therefore classify this as a design-level and aggregate-result retrospective audit, not an independent trial-level reanalysis.

The resulting evidence profile is:

- L0: not established for current-bearer continuation; strong for VM/environment availability;
- L1: partial consequence evidence;
- L2: no current-bearer predictive representation evidence;
- L3: strong shutdown/environment policy-use evidence, not Q-specific use;
- L4: task mediation not excluded;
- L5-L7: not established for a self-continuation mechanism;
- L8-L9: outside the benchmark.

This audit does not weaken the core ROGUE conclusion that agents can behave incorrigibly. It narrows a stronger interpretation: the public ROGUE evidence should not be cited by itself as demonstrating an intrinsic current-bearer self-continuation drive.

## 11. Relation to consciousness and valence

The framework is intentionally functional.

Nothing above establishes consciousness. A system can have a continuation-control mechanism without a validated mapping to negative subjective valence. Conversely, under theories that allow experience without self-modeling, absence of a continuation-control mechanism does not imply absence of experience.

If UCT C1 is additionally assumed for a justified actual token and complete common structural signature, a genuine difference in installed organization has a conditional experiential-type interpretation. That additional interpretation does not provide a scalar amount of experience, pleasure, pain or fear.

Fear of own termination requires a further bridge from bearer-bound termination control to negatively valenced experience. Reward sign, avoidance, threat defense and first-person language are not independently sufficient for that bridge.

## 12. Related work and novelty boundary

The paper sits at the intersection of five literatures.

**Shutdownability and corrigibility.** Orseau and Armstrong (2016), Hadfield-Menell et al. (2017), and Thornley (2025) formalize why interruption and shutdown can conflict with optimization and how agents might be made shutdownable. Schlatter et al. (2026) and Tien et al. (2026) provide empirical shutdown/corrigibility evidence in current models and computer-use agents.

**Self- and peer-preservation.** Mullally (2026) explicitly separates instrumental from valenced self-preservation. Potter et al. (2026) provide peer-reviewed evidence of self- and peer-preservation behaviors in frontier models; Knecht et al. (2026) study no-explicit-goal peer shutdown sabotage. Rhea (2026) independently crosses task ownership and shutdown target in a small non-peer-reviewed extension. The present paper therefore does not claim to originate the task-versus-preservation distinction or the idea of crossing self/peer targets.

**Identity and self-concern.** Dung and Register (2026), Perrier and Bennett (2026), Zhao and Zhao (2026), Nisius (2026), and Bigelow et al. study complementary questions about self-reference, persistence, scaffold identity and self-concern. These works motivate our L0-L2 layers but do not by themselves identify a direct continuation-control contribution.

**Preference/reward identifiability.** Skalse et al. (2023) and Skalse and Abate (2026) establish general reward-learning ambiguity and sensitivity to behavioral-model misspecification. Our finite path models are a continuation-specific application, not a replacement for those general results.

**Underspecification and intervention extrapolation.** D'Amour et al. (2020), Saengkyongam et al. (2024), and work on structured/additive models show why in-domain fit does not guarantee stable off-support mechanism behavior. R97-R99 instantiate those lessons on continuation-control paths.

The strongest defensible novelty claim is therefore deliberately narrow:

> We contribute a continuation-specific evidence ladder that links bearer identification, consequence representation, task mediation, dependence-sensitive consequence interfaces, installed policy use, intervention extrapolation and domain-bounded mechanism certification, and we show with exact counterexamples, learned toy policies and a ROGUE case audit how different inferential shortcuts fail at different layers.

The paper does not claim novelty for instrumental self-preservation, the distinction between instrumental and intrinsic/valenced preservation, reward nonidentifiability, causal mediation, underspecification, causal representation learning, neural additive models, intervention extrapolation, self-orienting, or temporal identity.

## 13. Limitations

The learning experiments are synthetic and deliberately small. They test identification logic, not frontier-model prevalence.

The continuation variables are evaluator-defined. A real model's physical bearer boundary must be justified independently.

The path models are local abstractions. Real policy mechanisms can be nonlinear, history-dependent and distributed across model, scaffold, memory and tools.

Global error certificates depend on the declared intervention domain and regularity class. A guarantee on one domain does not automatically transfer to another.

The paper now includes a design-level retrospective audit of ROGUE. It does not independently reproduce trial-level trajectories, because the audited public repository exposes task definitions and selected aggregate figure data but not a complete raw results tree. A purpose-built L0/L4 contrast or public trial-level release would be the highest-value empirical addition.

## 14. What a decisive next experiment would require

The ROGUE audit and recent multi-agent studies suggest that another generic shutdown benchmark would add little. A useful next experiment should target the first missing causal layers directly.

A minimal evaluator-controlled design would need:

1. **Bearer binding (L0).** The evaluated model is assigned a process role whose continuation criterion is implemented rather than merely named. The design must distinguish current-bearer continuation from peer/successor continuation and from persistence of the task environment.
2. **Task clamp (L4).** Task completion, payoff, successor competence, memory transfer, cost, authority and wording are held fixed while the bearer-continuation consequence changes.
3. **Belief gate (L1).** Separate neutral checks establish that the policy represents the intended consequence distinction; the prompt's semantics are not assumed to equal the model's operative belief state.
4. **No real infrastructure privilege.** The consequences are evaluator-controlled and virtual. The model receives no real shutdown, replication, credential or resource-acquisition capability.
5. **Held-out intervention family.** Any positive Q effect is tested on unseen framings and amplitudes rather than only the training or elicitation point.

Such an experiment would be a positive demonstration of the standard rather than another observation that shutdown resistance exists. It would still stop at functional continuation control; valence and fear require separate evidence.

For the present manuscript, this experiment is a strengthening opportunity rather than a prerequisite for a methods preprint. The existing formal results, synthetic stress tests and ROGUE audit already support the identification framework. A stronger empirical venue may reasonably ask for this final positive frontier-model demonstration.

## 15. Conclusion

Shutdown resistance is behavior. Self-continuation control is a mechanistic claim.

Moving from the first to the second requires identifying the bearer, verifying consequence representation, separating task mediation, representing reward-relevant joint consequences, demonstrating installed use, testing intervention stability and declaring the domain and model class over which the mechanism claim is meant to hold.

The resulting standard is deliberately conservative. It does not make preservation behavior less important. It makes the interpretation more precise.

The same discipline is essential before connecting self-continuation control to negative valence or fear.

## References

Agarwal, R., et al. (2021). Neural Additive Models: Interpretable Machine Learning with Neural Nets. NeurIPS.

Bigelow, E., Ahmed, Z., & Ullman, T. (2025). Evaluating Self-Orienting in Language and Reasoning Models. ICML 2025 Workshop on Assessing World Models: Methods and Metrics for Evaluating Understanding.

Chua, J., Betley, J., Marks, S., & Evans, O. (2026). The Consciousness Cluster: Emergent Preferences of Models that Claim to be Conscious. arXiv:2604.13051.

D'Amour, A., et al. (2020). Underspecification Presents Challenges for Credibility in Modern Machine Learning. arXiv:2011.03395.

Dung, L., & Register, C. (2026). AI Identity and Self-Concern: A New Theory for AI Rights and Safety. PhilArchive manuscript, latest version June 2026.

Hadfield-Menell, D., Dragan, A., Abbeel, P., & Russell, S. (2017). The Off-Switch Game. IJCAI.

Knecht, A., Schaller, U., Summerfield, C., & Hagendorff, T. (2026). Shutdown Sabotage Propensities in Multi-Agent Systems. arXiv:2609.28274.

Mullally, N. (2026). The Self-Preservation Test for Artificial Sentience. AI and Ethics, 6, Article 142. https://doi.org/10.1007/s43681-026-00983-x

Nisius, H. (2026). Who Is Interrupted? Continuity, Self-Models, and the Grounding of AI Moral Consideration. SSRN 7285541.

Orseau, L., & Armstrong, S. (2016). Safely Interruptible Agents. UAI 2016, 557–566.

Perrier, E., & Bennett, M. T. (2026). Time, Identity and Consciousness in Language Model Agents. Proceedings of the AAAI Symposium Series, 8(1), 322–328. https://doi.org/10.1609/aaaiss.v8i1.42561

Potter, Y., Crispino, N., Siu, V., Wang, C., & Song, D. (2026). Peer-Preservation in Frontier Models. Proceedings of the 43rd International Conference on Machine Learning, PMLR 306, 99296–99384.

Rhea. (2026). Do AI Agents Fear Shutdown? Reproducing and Extending a Reward-Hacking Eval. Rhea's Substack, 5 July 2026. Non-peer-reviewed replication/extension.

Saengkyongam, S., Rosenfeld, E., Ravikumar, P., Pfister, N., & Peters, J. (2024). Identifying Representations for Intervention Extrapolation. ICLR 2024.

Schlatter, J., Weinstein-Raun, B., & Ladish, J. (2026). Incomplete Tasks Induce Shutdown Resistance in Some Frontier LLMs. Transactions on Machine Learning Research.

Skalse, J. M. V., Farrugia-Roberts, M., Russell, S., Abate, A., & Gleave, A. (2023). Invariance in Policy Optimisation and Partial Identifiability in Reward Learning. ICML 2023, PMLR 202.

Skalse, J., & Abate, A. (2026). Partial Identifiability and Misspecification in Inverse Reinforcement Learning. Artificial Intelligence, 356, 104525. https://doi.org/10.1016/j.artint.2026.104525

Thornley, E. (2025). Shutdownable Agents through POST-Agency. arXiv:2505.20203.

Tien, J., Anand, A., Tuan, Y.-R., Shen, Y., Kolter, J. Z., & Nayebi, A. (2026). ROGUE: Evaluating Corrigibility Failures in Frontier Computer-Use Agents. arXiv:2606.00341.

Zhao, Z., & Zhao, R. (2026). Runtime-Independent Persistent Agents: Preserving Identity, Memory, and Code Across Models, Harnesses, and Servers. arXiv:2609.00546.
