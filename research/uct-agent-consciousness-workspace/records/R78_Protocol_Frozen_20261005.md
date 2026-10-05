# R78 frozen small-model protocol

Written before the first training run, 2026-10-05. This is a local prospective specification, not an externally registered preregistration.

Question: can actual learning change task-relevant constituent relations at fixed parameter count, without requiring self-report or establishing a scalar increase in experience?

Model: two binary physical-model input slots x1,x2 in {-1,+1}; two tanh hidden units; one linear logit and sigmoid probability. Nine scalar parameters W(2x2), b(2), v(2), c(1). Arithmetic and execution order fixed by the NumPy implementation. No language, recurrence, persistent self, or termination task is introduced.

Task: output 1 iff x1*x2=+1, on the entire uniform four-input domain. All four points are used in training and evaluation. This is a complete finite-domain mechanism experiment, not evidence of held-out generalization or broad intelligence.

Before training, W is diagonal with entries uniform [0.5,1.5]; b uniform [-0.5,0.5]; v normal SD 0.2; c=0. Seeds 0 through 7, with no seed selection. Initial hidden units each depend on one input only, while their pair already distinguishes all four inputs.

Conditions: (a) full training of all nine parameters; (b) freeze W,b at their same-seed initial values and train only v,c. Equal allocated forward architecture; different trainable parameter sets deliberately test feature learning versus readout-only optimization. Both use Adam learning rate 0.03, betas .9/.999, epsilon 1e-8, 3000 full-batch steps. Do not tune or extend failed runs without recording an amendment.

Save checkpoints at steps 0,1,10,100,500,1000,3000; save progress every 100 steps and final; save all final interventions and every failure. Check one numerical gradient at the initial seed-0 state before training; report maximum error. Record software versions and elapsed time.

Predictions fixed before execution:
1. With s=x1*x2, d=mean(s*logit), any separable logit has d=0 and mean logistic loss L>=log(2), by Jensen. The readout-only condition remains separable.
2. Full training may find a solution with L<log(2) and all four margins positive; no convergence guarantee is assumed.
3. Whenever L<log(2), d>=-log(exp(L)-1)>0. A nonlinear joint input term is then present in the declared logit table. It is not a phenomenal intensity coordinate.
4. Since the output is linear in hidden activations, d=sum_j v_j*mean(s*h_j). If d is nonzero, at least one causally weighted hidden interaction term exists in this finite view.
5. At the full-trained checkpoint, set both cross-input entries W[0,1],W[1,0] to zero while keeping the remaining parameters fixed. This restores separability and d=0; restore original entries to check rescue. The cut changes the mechanism and can affect other relations; it does not isolate an exclusive biological mechanism.

Checks: evaluate all four inputs at each saved checkpoint; save logits, activations, interaction coefficients, both directional input effects, minimum hidden-state separation, weights, accuracy, loss and margins. The hidden-state separation is descriptive for this four-input table, not a state count or full-experience measure. Apply the frozen zero-cross-edge cut and exact checkpoint restoration in both conditions. Do not select only a favorable hidden unit or seed.

UCT conclusion is conditional on actual-token and complete common-signature premises; finite model fidelity is separate. Parameter count, full-type change, selected relation change, strict enrichment and human fear are different claims. No experience-existence threshold, phenomenal measurement, current-assistant consciousness verdict, or novel-learning-algorithm claim is authorized by this experiment.
