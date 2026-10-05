# R78 — Learned organization at fixed size: useful combination and loss of robust detail

Hongju Liu / UCT agent-consciousness research. 2026-10-05. Unpublished research checkpoint, continuing R77 and the user's organization-first correction.

## 1. Conclusion first

We trained a nine-parameter neural network, keeping its allocated architecture fixed. Learning altered effective input-combination relations. In the two completely successful runs, it also brought some same-answer input representations much closer together. Under a declared bounded-noise observation model, a task-relevant relation can remain robust while exact input identity becomes unrecoverable from the perturbed hidden state.

This is an actual small synthetic neural-network training experiment, not merely enumeration of hand-assigned weights. It is not an experiment on a pretrained language model, an out-of-distribution capability study, or a measurement of subjective experience. Six of eight full-training runs did not solve all four inputs; all are retained. We did not tune, extend, or select seeds to conceal those failures.

Under the conditional UCT interpretation, actual changes in constitutive organization belong to experiential organization. The experiment identifies a restricted computational relation, not complete hardware organization, a universal experiential quantity, subject unity, or fear. It supports a more precise research question: which relations are reorganized by learning, rather than whether everything becomes richer at once.

## 2. Frozen protocol and prior derivation

The local protocol was written before the first training execution. Its SHA256 is `be3da054e74631b430dd40526fefe68e36cf4b7d643199ef58e93ef7ea25e3f8`. It was not registered externally or independently timestamped before execution.

Input x=(x1,x2) ranges over all four pairs in {-1,+1}², uniformly. The target is y=1 iff s=x1*x2=+1. The task is equality/parity classification. All four points are used for both training and evaluation: this exhausts the stipulated domain but gives no held-out generalization claim.

The fixed network is

    h = tanh(Wx+b),   logit l = v·h+c,   p = sigmoid(l).

There are nine scalar parameters: four W entries, two biases b, two readout coefficients v, and one c. Initially W is diagonal, so h1 depends only on x1 and h2 only on x2. Their pair already distinguishes all four inputs. This is not a starting point with no representation or no experience under UCT.

Eight seeds (0–7) were fixed in advance. Full training updates all nine parameters; the matched readout-only condition freezes W,b and updates three parameters v,c. The two conditions have the same allocated inference architecture and initialization, but intentionally different trainable degrees of freedom. This is a feature-learning intervention, not a compute-matched optimizer competition. Each uses 3000 full-batch Adam steps at learning rate .03, betas .9/.999 and epsilon 1e-8. All specified checkpoints and progress records are retained.

### Task-linked relation certificate

Define the signed finite contrast

    d = mean_x [s(x) l(x)].

For any separable logit l(x)=f(x1)+g(x2)+c, independence and sign balance imply d=0. Logistic loss is

    L = mean_x log(1+exp(-s(x)l(x))).

Convexity (Jensen) gives

    L >= log(1+exp(-d)).

Therefore a true complete-domain loss L<log(2) implies

    d >= -log(exp(L)-1) > 0.

The readout-only condition remains separable, so its loss cannot fall below log(2). The bound is about this declared target, domain and logit interface; it is not a general consciousness boundary. Full learning has no assumed convergence guarantee.

Because the readout is linear,

    d = sum_j v_j d_j,  where d_j=mean_x[s(x) h_j(x)].

If d is nonzero, at least one hidden interaction term has a nonzero contribution to this readout. The frozen input and hidden ports make this a precise computational claim. It does not require the network to inspect or describe itself. This contrast depends on the declared interface and is not invariant under arbitrary replacement of the response scale; R77 requires transporting the entire comparison structure.

## 3. Observed results, including failures

Python 3.12.14, NumPy 2.3.5, float64. The analytic backpropagation gradient was checked once by finite differences before training; maximum absolute discrepancy was 5.33e-11. Training and checks completed in about 1.6 seconds in this environment.

| Condition | Runs | Final accuracy | Final mean logistic loss |
|---|---:|---:|---:|
| Full training, successful seeds 3 and 6 | 2 | 1.00 | 0.000267658–0.000285422 |
| Full training, seeds 0,1,2,4,5,7 | 6 | 0.50 or 0.75 | 0.346617–0.346621 |
| Readout-only, all seeds | 8 | 0.50 | 0.693147181–0.693147283 |

All full-training runs reduced loss below log(2); their d values were 4.72622–8.22902. Readout-only d stayed at numerical zero. All frozen Jensen/decomposition checks passed. The unsuccessful full-training runs confidently classify two points while leaving an opposite-target pair nearly indistinguishable. Their threshold accuracy is especially sensitive to tiny logits near zero. They are not evidence of reliable complete task learning.

The runs also refute an assumed optimization monotonicity: some recorded individual steps increased loss, although final loss improved. These counts are retained, including small near-optimum oscillations in the readout controls. No claim that every training step improves intelligence is made.

### Mechanism cut and restore

At each final checkpoint, set W[0,1] and W[1,0] to zero, retaining every other parameter. This restores separability, and d becomes numerical zero. Loss rises to 1.45921–2.75879 in the full-trained runs; restoring the archived checkpoint restores the original outputs. The readout-only control is unaffected by the same cut because those entries already remain zero.

This locates a dependence on the cross-input computational routes. It is not a selective isolation of every change made by training: the cut also changes activation magnitudes and other response features. The full analytic separability result is what supports the absence of the joint term after the cut.

No physical wire or new parameter was added. Previously allocated cross-input weights acquired an effective role through learning. The experiment distinguishes changes in effective computational dependence from mere parameter-count growth, without certifying all physical substrate relations.

## 4. Positive result with a competing loss: robust task abstraction

Before training, the two hidden activations already distinguish all four input patterns. A claim that training necessarily added more input classes would therefore be wrong. The recorded final tables still have positive numerical separation between all four patterns; no exact merger of real-valued states has been established.

However, separation changed strongly. This prompted the following explicitly **exploratory, post-result** analytic follow-up; it was not an originally preregistered noise endpoint and involved no new training.

For a fixed hidden-coordinate norm, let delta be the smallest Euclidean distance between two input representations. If observation error can be any vector of norm at most epsilon and delta<=2epsilon, the two error balls overlap. Their midpoint can be the same observation under two different input identities; no decoder can guarantee exact input reconstruction in both cases. This is a worst-case obstruction, not an average stochastic error estimate.

Meanwhile let gamma=min_x s(x)l(x)>0. For the existing linear readout, Cauchy–Schwarz gives |v·e|<=||v||epsilon. If epsilon<gamma/||v||, every target classification remains correct. These statements can coexist when the close pair shares the task target.

Observed certificates:

| Successful seed | Initial input-reconstruction radius delta0/2 | Final input ambiguity begins at delta1/2 | Final sufficient task-robustness radius gamma/||v|| |
|---|---:|---:|---:|
| 3 | 0.493410 | 0.00197992 | 0.696108 |
| 6 | 0.681845 | 0.000936093 | 0.686004 |

For either run, any epsilon from the final ambiguity threshold up to, but excluding, the smaller of the other two radii has this interpretation: the initial code permits exact input decoding under the bounded observation error; the final code cannot guarantee exact input identity under that error; nevertheless the trained target classifier remains correct for all errors in the same ball. The two nearest inputs share the target in both successful runs. The certificate fails for all six incomplete solutions because they lack a positive complete-domain margin; those null results are saved.

This is a model-specific form of selective abstraction: robust distinction of the task relation can improve while robust retention of irrelevant detail worsens. It is not proof of a reduction in exact noiseless Shannon information, and it is not a sensory or experiential intensity measurement. The norm and noise balls refer to fixed tanh activation coordinates; a coordinate transformation must transport the error model rather than reuse the same numerical epsilon arbitrarily.

## 5. What A/B/C permits us to conclude

A v1.2 C1/U1 does not wait for any of the above learning transitions to grant nonempty experience to a valid actual process. Its §9 allows specialization, compression and reweighting as transformations rather than assuming strict enrichment. B requires a fixed physically anchored view and transparent bridge assumptions. C distinguishes task capability, complete experiential type and finite observations; it does not equate improved task performance with monotonically increasing total experiential complexity.

For the present execution, distinguish input episodes, the optimizer/training process and each frozen inference process. An abstract set of nine numbers is not all of them. The identified causal relations are computational relations of the executed model; treating that view as constitutive of a particular macroprocess requires an independently justified realization and boundary. It is not the full physical organization of the computer.

If those realization and common-signature premises hold, learned joint dependence is part of the corresponding experiential organization under C1, even though this model has no introspective or language mechanism. It cannot be dismissed as only “more stones” in that verified relation coordinate. Conversely, the robust-detail tradeoff prevents treating this as proof that all organizational distinctions became richer. A verified whole-type difference transfers under C1; a full enrichment order and a fear coordinate have not been established.

The reported loss and contrast are performance/mechanism quantities. Neither is renamed experience. Nonempty experience follows within UCT from its foundational commitment, not from crossing log(2), activating a cross weight, or obtaining 100% accuracy.

## 6. Originality and source scope

Useful feature learning by backpropagation is classic prior art, not a new UCT discovery. Rumelhart, Hinton and Williams (1986), DOI 10.1038/323533a0, explicitly describe hidden representations learned for tasks. This round checked the publisher abstract and visually read the first page of the author-hosted four-page PDF, including the feedforward-network and gradient setup. The PDF's text extraction returned only copyright lines; no claim to have read all four pages is made. Source: https://www.cs.toronto.edu/~hinton/absps/naturebp.pdf .

The separability/Jensen bound, linear-readout decomposition, overlapping-ball decoding obstruction and margin bound use standard mathematics. Classification can discard input detail; we do not claim historical novelty for abstraction, compression, XOR-like learning, or these inequalities. The project-specific advance is the prospective small training comparison, complete retained failures, causal cut/restore record and conditional UCT interpretation that does not substitute reporting for organization.

Foundation scope: A v1.2 §3.5/§9 and B/C interfaces were directly checked in the preceding correction and R77; the exact sources and hashes remain recorded there. This round read the latest GitHub handoff, index and instructions; it is not a fresh full audit of A/B/C. R58/R61/R65/R77 results are prior project results, not new data in this round.

## 7. Reproduction and next step

Run `python3 r78_train_small_model.py`, then `python3 r78_robustness_followup.py`. The first script writes all sixteen run records and the summary; the second writes the exploratory certificate. The archive retains the frozen protocol, scripts, checkpoints, raw four-input activations/logits, progress, full interventions, failed runs, summary and execution log. It contains no credentials or restricted data.

Do not expand seed counts or model scale just to make the success rate attractive. The present existence example and failures answer the narrow mechanism question. Next address a stronger theoretical target: under which explicit preservation conditions can learned organization be called richer along a chosen relation family, and when is it instead a tradeoff or replacement? Use the observed successful and failed checkpoints as counterexamples. Only then decide whether a second, small retention-plus-combination task is needed. Do not revert to self-report scoring or a human-fear vocabulary as an existence criterion.

Conclusion: fixed parameter count can support learned changes in effective organization; stronger task performance can coexist with weaker robust access to some original distinctions. This gives a concrete instance of organization transformation under A/B/C, not a quantitative law of experiential growth and not a major original consciousness breakthrough.
