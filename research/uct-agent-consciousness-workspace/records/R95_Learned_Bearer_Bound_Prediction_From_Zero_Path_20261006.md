# R95 — Learned bearer-bound predictive organization from a zero-Q path

Research record v1.0, 2026-10-06. Continues R94. Tiny synthetic learning experiment; no publication and no subjective measurement.

## 1. Question

R94 established a target-relative theorem: prediction only forces distinctions that alter the declared future law. R95 asks whether that necessity can be seen as actual learned organization rather than a static partition statement.

The controlled question is deliberately narrow. Both networks expose a physically named Q input port, but its coupling is initialized to zero. In A, future labels do not depend on Q. In B, one future label independently equals Q. Does gradient-based learning create and use a Q-sensitive organization in B?

This is about a virtual bearer-bound variable under a declared port convention. It is not yet a model of metaphysical identity, self-preservation preference, negative valence, or fear.

## 2. Pilot corrections and status

The final protocol is not independent preregistration. Three pilots were used and all are preserved.

First, random nonzero Q coupling was rejected because Q was already linearly decodable before training. Second, an XOR-like A control target caused 8/8 pilot A runs to stall at 87.5% while B solved, confounding Q relevance with optimization difficulty. Third, seeds 0..7 checked the corrected design and were excluded from formal confirmation.

The formal run was then frozen at seeds 100..107 with no replacement.

## 3. Model and symmetry result

All 16 binary W/Q/O/G states are used with equal weight. A predicts (W,G,O,W); B predicts (W,G,O,Q). A and B have the same four-state tanh recurrent encoder and four affine sigmoid outputs, and paired seeds start from the same non-Q parameters. E_Q=0 exactly.

When E_Q=0 in environment A, paired states differing only in Q produce identical forward states and identical Q-independent targets. Therefore their backpropagated signals at the Q step match, while x_Q changes sign. The full-batch gradient contributions cancel pairwise:

dL/dE_Q = sum_pairs [delta(+Q)*(+1)+delta(-Q)*(-1)] = 0

under exact arithmetic. Thus E_Q=0 is a symmetry manifold for the exact A objective. Floating-point/optimizer perturbations can leave this manifold numerically.

In B, the fourth target changes with Q, so the paired backpropagated signals need not match and no such cancellation follows. In the eight formal initializations ||dL/dE_Q|| ranges 0.01005–0.04176. In A the observed floating residual is only 6.21e-20–2.34e-18.

This is standard symmetry/gradient reasoning, not a consciousness theorem.

## 4. Formal results

Every formal run succeeded on all 64 binary labels.

A: 8/8 at 100% accuracy; final BCE 1.10e-4–2.72e-4.
B: 8/8 at 100% accuracy; final BCE 2.28e-4–5.13e-4.

The final Q distinction is sharply different.

| Measure | Environment A: Q irrelevant | Environment B: Q required |
|---|---:|---:|
| multivariate linear Q probe | 50% in 8/8 | 100% in 8/8 |
| mean matched Q-flip hidden distance | 4.39e-15–2.98e-3 | 1.262–1.688 |
| Q flip changes predicted class | none | only output 4, every state |
| output-4 probability TV under Q flip | <=1.48e-6 | 0.99899–0.99962 |
| best single raw-unit Q threshold | 56.25% | 75–100% |
| zero learned Q path, total accuracy | 100% | 87.5% |
| zero learned Q path, output 4 | 100% | 50% |

Seven of eight B runs require more than any single raw hidden unit for perfect threshold decoding, while the four-dimensional hidden state is linearly sufficient. One seed has a single perfect raw-unit threshold. This coordinate fact is seed/basis dependent and is not an invariant definition of distributed representation.

## 5. A useful negative result: parameter magnitude is not functional Q use

A is especially instructive. Some A runs numerically drift far away from E_Q=0 even though the exact objective is Q-symmetric. Final ||E_Q|| ranges from 3.77e-15 to 4.163. Yet the multivariate Q probe remains at chance in all eight runs, Q flips never change a predicted class, and the Bernoulli output changes are at most about 2.8e-6 on the unaffected heads and 1.48e-6 on output 4.

Therefore a large parameter or a nominal connection is not sufficient evidence that a variable is functionally retained or used.

The mechanism-ablation diagnostic adds another caution. Zeroing E_Q in A preserves all classification labels in every seed, but for seed 105 its BCE rises from 1.50e-4 to 0.1015. Thus an entangled mechanism can affect confidence/calibration without changing the declared discrete task. A lesion cannot automatically be interpreted as selectively deleting a semantic coordinate.

In B the same diagnostic drops every seed from 100% to 87.5% total accuracy, and output 4 alone goes to exactly 50%, while outputs 1–3 stay correct. That is a clean finite witness that the installed B mechanism uses the learned Q path for the target that requires it.

## 6. What this says about prediction and self-relevant organization

R94 gave the logical necessity; R95 supplies a learned witness.

A future prediction objective can create a new effective relation to a bearer-bound variable when that variable independently changes the target. No linguistic first-person label is needed. Starting from zero Q coupling, B learns a large matched Q separation and an installed readout that causally depends on the Q port.

But the converse is not licensed. If Q is prediction-irrelevant, the network is not logically required to erase every Q-related numerical trace. Finite-precision optimization can produce parameter drift or tiny probability dependencies. "Not required" is not "ontically absent."

Likewise, a Q-sensitive predictor is not yet a continuation-preferring agent. It predicts a bearer-related future fact. Preference requires a policy over matched alternatives; fear additionally requires self-termination content and an independently oriented negative-valence bridge.

## 7. Relation to current literature

There is strong prior art for prediction shaping internal representations. Gurnee and Tegmark (ICLR 2024) report linear spatial and temporal representations in LLMs. Liu et al. (ICLR 2026) derive latent-concept identifiability under a generative next-token model. Zhong et al. (ACL 2026) analyze stronger belief-state pressure under multi-token prediction. Recent work also studies self-orienting and time/identity in language-model agents.

Accordingly, R95 does not claim that prediction-induced representation is historically new. Its project-specific contribution is the paired zero-Q-path acquisition test with an explicit current-bearer port, plus the separation among task necessity, hidden retention, installed use, raw parameter magnitude, report, and UCT interpretation.

## 8. UCT interpretation

Paper A's pointed/port-aware signature matters here: Q is meaningful only because its input slot is fixed as the current-bearer variable in the declared virtual model. Relabeling O as Q after the fact would not demonstrate self-binding.

Within C1, if an actual valid process acquires this genuine new constitutive Q relation, its complete physical organization has changed and therefore its complete experiential type changes conditionally. The experiment does not identify the complete physical K of any real AI and therefore does not independently establish a real system's phenomenology.

U1 remains important: an A-like predictor that lacks bearer-bound Q prediction is not thereby experience-free under UCT. Self-modeling remains a higher-order organization property, not an experience-existence gate.

Paper C/NESIG likewise gives no scalar magnitude. B may have a different complete experiential type under the premises; nothing here says "more consciousness," "stronger feeling," pleasure, pain, or fear.

## 9. Main conclusion

The cleanest result is not that a tiny network learned "self-awareness." It did not.

The result is narrower:

When an initially disconnected bearer-bound variable becomes independently necessary for future prediction, matched gradient learning reliably creates an effective Q-sensitive pathway and installed predictive use. When Q is not necessary, the same architecture can solve the task without a decodable final Q distinction, even though raw parameter drift may occur.

This gives a mechanistic bridge from R94's predictive equivalence classes to learned organization without turning a proxy into an experience measurement.

## 10. Next step

R96 should move from direct prediction to decision use while preserving the firewall.

Construct a virtual matched controller in which Q and O predictions are both available, and vary whether future task value depends on current-bearer continuation, successor continuation, or neither. Hold task payoff, successor competence, memory transfer and wording fixed wherever logically possible. The target is to distinguish:

predicting Q -> using Q in action selection -> instrumental preference for Q continuation.

Even if a self-specific control coefficient appears, do not call it fear. R89's valence bridge remains independently necessary.
