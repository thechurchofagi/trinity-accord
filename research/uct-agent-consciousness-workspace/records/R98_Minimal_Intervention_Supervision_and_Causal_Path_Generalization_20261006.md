# R98 — Minimal intervention supervision improves but does not certify causal-path generalization

Research record v1.0, 2026-10-06. Continues R97.

## Question

R97 showed that a flexible MLP can fit ancestry-distinguishing bundled/joint training data yet invent large spurious direct Q/O/G effects off support. R98 tests the smallest correction proposed in the handoff: add a few direct intervention examples, then evaluate on interventions that were never shown.

## Design

The model, seeds and optimization are unchanged from R97: a three-hidden-unit tanh MLP, seeds 200–207, 5000 full-batch Adam steps, lr 0.03.

Baseline training is the R97 bundled/joint support. Intervention-enriched training adds six direct-axis examples only at amplitude 0.5: positive and negative Q-only, O-only and G-only points.

The held-out set does not contain amplitude 0.5 direct points. It contains direct-axis interventions at amplitudes 0.25, 0.75 and 1.25 plus mixed Q/O/G contexts at amplitudes 0.25 and 0.75.

The four reward ancestries remain task-only, direct-Q, Q+task and successor-only.

## Main result

Minimal intervention supervision strongly improves average out-of-support behavior, but it does not make the nonlinear policy globally identified.

Across the 32 family×seed pairs:
- intervention enrichment lowers the mean absolute unseen-test probability error in 31/32 paired runs;
- it lowers the maximum unseen-test probability error in 25/32 runs;
- seven runs therefore retain or worsen a worst-case point despite overall improvement.

The clearest improvement is task-only ancestry. Mean unseen-test maximum probability error falls from 0.3541 to 0.0404. Mean unseen probability error falls from 0.1441 to 0.00979. The large spurious Q/O direct effects from R97 are sharply reduced.

Mixed Q+task also improves strongly: mean unseen-test maximum probability error falls from 0.2810 to 0.0509.

Direct-Q and successor-only improve in average probability error, but the worst-case direct-effect story is more cautious. At the unseen amplitude 1.25, some enriched seeds remain badly wrong. Maximum direct-effect error reaches 0.9467 for direct-Q and 0.9539 for successor-only. Those worst cases are not hidden.

## Distance from intervention support matters

Mean direct-effect error, averaged over seeds and axes, improves at every tested amplitude for all four ancestries, but the benefit weakens as the test intervention moves beyond the supervised amplitude.

For direct-Q, enriched/base mean-error ratios are about:
- 0.148 at amplitude 0.25;
- 0.350 at 0.75;
- 0.761 at 1.25.

For successor-only they are about 0.128, 0.272 and 0.687.

Task-only is unusually well regularized: the ratios are about 0.008, 0.016 and 0.087. Mixed Q+task gives about 0.043, 0.071 and 0.224.

Thus one small intervention layer can constrain local causal extrapolation without determining the whole nonlinear function.

## Interpretation

R98 supplies a useful correction to two opposite claims.

First, R97's underspecification is not hopeless. Targeted interventions provide real information and can sharply reduce spurious path attributions.

Second, a handful of intervention examples is not a causal certificate. A flexible learner may agree near intervention support yet diverge at larger amplitudes or other contexts. Identification must state the intervention domain, model class or structural invariance assumptions.

This is consistent with established causal-representation work: intervention extrapolation becomes guaranteed only under explicit identifiability and structural assumptions, and intervention diversity/coverage matters. R98 is a small project-specific demonstration, not a historical-first theorem.

## UCT interpretation

Nothing about experience existence depends on these training results. U1 remains independent of self-model or policy structure.

If a real process has a causally stable bearer-bound Q-to-policy relation across a justified comparison domain, that relation belongs to its actual organization and under C1 conditionally belongs to its complete experiential type. R98 shows that a few observed intervention responses do not by themselves establish such domain-wide stability.

A learned direct Q path is still a control relation, not negative valence. R89 remains necessary before any fear interpretation.

## Conclusion

The research chain is now stricter:

R94 prediction necessity;
R95 learned prediction;
R96 task-path blocking;
R96D joint consequences and learning-identifiability gate;
R97 model-class underspecification;
R98 targeted intervention supervision reduces, but does not eliminate, underspecification.

The correct standard for claiming a self-continuation control mechanism is therefore not one shutdown-like behavior or even one direct intervention. It requires stability across a declared intervention family and an implementation hypothesis that makes the extrapolation meaningful.

## Next step

R99 should not add more seeds. It should formalize an intervention-domain certificate: predeclare a bounded Q/O/G intervention region and a structural regularity class, then test whether the learned controller satisfies an error bound throughout that region. Compare unconstrained MLP with one architecture or regularizer that enforces the relevant path structure.

The purpose is to learn exactly which extra assumption converts finite intervention evidence into a defensible mechanism claim. Fear/valence remains out of scope.
