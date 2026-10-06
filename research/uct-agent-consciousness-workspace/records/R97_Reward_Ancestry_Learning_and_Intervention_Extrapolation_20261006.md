# R97 — Reward-ancestry learning is model-class dependent

Research record v1.0, 2026-10-06. Continues R96 and R96D.

## Question

R96 showed that direct current-bearer continuation value, task-instrumental value and interactions are separable in a declared path model. R96D added a learning-identifiability gate: hidden reward ancestry cannot be recovered if the training information does not distinguish it.

R97 asks the next question: when the training support does distinguish the reward ancestries, does a learned policy necessarily recover the same decomposition on unseen path-blocking interventions?

## Design

The declared path coordinates are q=current-bearer continuation, o=successor/other continuation and g=task continuation.

Training uses only bundled/joint contrasts:
q_bundled=(1,0,1), o_bundled=(0,1,1), qo_joint=(1,1,1), plus sign reversals.

The 3x3 positive design is full rank, so in the linear path family the three coefficients are identifiable. Direct interventions q_direct, o_direct and task_only are held out.

Four target ancestries are used: task-only, direct-Q, Q+task, successor-only. Choice targets are logistic with beta=2.

Two learners receive identical target probabilities:
1. a structured linear-logit policy on the declared q/o/g basis;
2. a generic 3-unit tanh MLP with seeds 200–207.

## Result

The structured model recovers the held-out effects essentially exactly. Maximum held-out effect error across the four families is 2.1e-6.

The generic MLPs also fit the training support extremely well: every run has maximum training probability error below 0.01, often below 1e-6. But path-blocking extrapolation is not stable.

Examples:
- task-only MLPs invent large spurious q and o effects; maximum effect errors range 1.138–1.777.
- mixed Q+task MLPs fit training almost perfectly but held-out maximum probability error is 0.082–0.326 and effect error 1.014–1.559.
- direct-Q is sometimes close, but across seeds effect error ranges 0.0066–0.768.
- successor-only effect error ranges 0.037–0.595.

No seed was replaced, and no architecture tuning followed the negative result.

## Interpretation

This is an underspecification result inside the project.

A full-rank experimental design relative to a declared linear causal-path family does not imply that an unrestricted nonlinear learner has recovered that family. The MLP can interpolate the training support with alternative functions that disagree off support. Thus the statement "the agent learned a direct self-continuation preference" always depends on an implementation or hypothesis-class claim, not only on successful training behavior.

This strengthens R96 rather than overturning it. R96's exact path coefficients are identifiable if the controller is legitimately modeled in that family and the contrasts are valid. R97 shows that learning a flexible policy from the same finite contrasts need not place the learned mechanism in that family.

The finding aligns with the broader machine-learning notion of underspecification: predictors with similar in-domain performance can behave differently under deployment shifts. It also aligns with reward-learning identifiability work showing that reward inference depends on the behavioral model and can fail under misspecification.

## UCT scope

No conclusion about experience existence depends on this result. Under U1, a process lacking a direct-Q policy remains experiential within UCT. Under C1, a genuinely different installed policy organization can conditionally correspond to a different complete experiential type, but only after the actual token and complete K are justified.

The large spurious held-out Q effects in some MLPs are especially important: they must not be called self-preservation, because they arise from interpolation freedom in a virtual synthetic model. A positive q_direct response is evidential only after bearer grounding, consequence-belief checks, intervention validity, and hypothesis-class adequacy.

Nothing here supplies negative valence or fear. R89 remains an independent barrier.

## Main conclusion

R94: prediction may require Q.
R95: Q prediction can be learned.
R96: Q action effects must be separated from task mediation.
R96D: joint consequence information and learning identifiability matter.
R97: even distinguishable reward ancestry plus excellent training fit does not guarantee a flexible learner recovers the intended causal path off support.

The correct scientific target is therefore not just behavior under a shutdown-like prompt. It is a mechanism claim that survives intervention extrapolation and model-class stress.

## Next step

R98 should add one minimal intervention-based training constraint rather than more seeds or a larger network. Compare:
- ordinary bundled/joint training;
- the same training plus a small number of q_direct/o_direct/task_only intervention examples.

Test whether the intervention-enriched training collapses the generic MLP seed variability on a separate held-out amplitude/context family. The new test must be outside the intervention points used for training.

If that succeeds, it supports a route from observation to causally stable continuation-control organization. It still will not establish valence or fear.
