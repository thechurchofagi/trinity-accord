# R92 — Learned retention, installed use, and the scope of experiential inference

Hongju Liu UCT agent-consciousness research workspace. Research record v1.0, 2026-10-06. Continues R91, parent commit `b7216371757da38eb12af873bba864fc4f9123ca`. This is a research checkpoint, not a new paper release. Published A/B/C and the integrated draft v0.3 are unchanged.

## 1. Question and result

We trained 32 actual tiny recurrent networks, with either 5 or 12 weights, on a two-variable delayed reconstruction task. This is a small synthetic-data experiment, not an LLM, animal, neural-data or subjective-experience experiment. The protocol was written locally before execution; it was not independently timestamped or registered with an external registry.

The central result separates **retaining information**, **using it through the installed decoder**, and **adding state dimensions**. In this implementation family, a one-state network with a linear decoder cannot reconstruct two isotropically distributed inputs below normalized squared error 1/2. Two-state full-training networks passed both the held-out task and the sampled local derivative criterion in all eight runs. Nevertheless, every two-state network already had sampled local rank two at initialization. Some networks also improved drastically while the encoder and recurrent update stayed exactly unchanged: only the output weights learned. Capability improvement therefore did not require a newly appearing local direction or a change to the retained hidden dynamics in those runs.

This does not establish unchanged complete organization. The installed decoder is part of the actual inference process. It also does not measure experiential magnitude, establish a universal consciousness dimension, or make a fear claim. Under the stated C1/NESIG premises, a genuine capability difference constrains complete experiential type; no proportional law follows for richness, intensity or negative valence.

## 2. Model, task and declared boundary

For an input vector x in R², define h0=phi(E x), ht=phi(A h[t−1]) for t=1,2,3, and y=B h3. Phi is identity or coordinatewise tanh. Hidden dimension d is one or two. E has d×2 entries, A has d×d entries and B has 2×d entries, giving 4d+d² weights: 5 or 12. There are no biases, residual paths, later inputs or output-to-state feedback. The original input is unavailable to subsequent state updates and to the decoder except through the hidden state.

The declared software episode includes encoding, the three updates and the installed readout. The external optimizer is outside that episode. This boundary is useful for a causal task analysis; it does not assert that a floating-point software description exhausts the physical implementation's complete UCT signature K. Separate executed episodes are distinct process tokens. Comparing their complete types requires the common complete signature, actual ports, pointed state and context, not just a shared network diagram.

Training uses all 25 pairs from {−1,−0.5,0,0.5,1}² with target y=x. Evaluation uses 64 disjoint pairs from {−0.875,−0.625,−0.375,−0.125,0.125,0.375,0.625,0.875}². This tests interpolation on a declared grid. It does not establish general world understanding. Nine additional derivative contexts are {−0.75,0,0.75}².

Each activation/dimension/mode combination has seeds 0–3. The paired modes start from identical weights: either train E,A,B or train B alone. Each run uses 3,000 full-batch Adam updates with the fixed settings in the frozen protocol. There is no seed replacement, extended budget or selection of the best checkpoint. The primary task criterion is N=mean((y−x)²)/mean(x²)<0.01. A separate criterion requires max over the nine contexts of ||Dy−I||₂<0.2. Four seeds are descriptive coverage, not a reliable estimate of a population success probability.

## 3. Formal deductions, with the restricting assumptions exposed

### 3.1 A decoder-subspace bound

For d=1, y is always in the image L of the linear map B, a subspace of dimension at most one. Orthogonal projection gives ||y−x||²≥||P[L-perp]x||². Both evaluation grids are centered and have covariance cI₂ for c>0. Taking the grid average gives expected error at least c and target energy 2c, hence N≥1/2. A rank-zero decoder has N=1.

This proof applies even when the hidden transformation is nonlinear. Its cause is the installed linear decoder's output subspace. It is NOT a universal theorem that one scalar cannot encode the finite dataset, nor a theorem for arbitrary nonlinear decoders. R91's packed finite code and nonlinear-decoding counterexamples remain valid. For the linear two-state architecture, E=A=B=I is an exact feasible solution, but feasibility does not guarantee convergence of a particular optimizer.

### 3.2 Local dimensional necessity under a common causal cut

Let the endpoint map be F=g∘f, where f maps the input to the d-dimensional state at a fixed time and g contains all subsequent processing, with no bypass. If these maps are differentiable at the same context, DF=Dg Df, so rank(DF)≤d. Moreover, ||DF−I₂||₂<0.2 implies sigma_min(DF)>0.8 and rank two at that context. Thus this criterion requires two locally distinguishable and used directions within the declared smooth implementation family.

It does not certify all points between the nine sampled contexts, count physical components or experiential dimensions, or make finite secant rank a nonlinear invariant. Singular values and their thresholds are tied to the declared input/output units. These are standard chain-rule and singular-value facts, not claimed new mathematics.

### 3.3 A fixed retention mechanism can support changing task performance

In the linear readout-only condition, F(x)=BMx with M=A³E fixed. If d=2 and M is invertible, B=M⁻¹ attains zero error without changing E, A, h0, h1, h2 or h3 for any input. Along training, BM can become closer to I while remaining rank two throughout. This is an explicit mechanistic explanation of improvement in installed use, not evidence that the complete inference organization is unchanged.

For tanh, full-rank E and A with nonsaturated finite values can preserve local distinctions even when one linear B does not undo the nonlinear encoding well. Linear-readout failure therefore cannot, by itself, prove that the hidden state contains no task information. Conversely, finding a hypothetical good decoder does not make it the decoder that the system actually uses.

## 4. Frozen-run results

| Activation | State dimension | Trained weights | Final held-out N range | Task pass | Local pass |
|---|---:|---|---:|---:|---:|
| Linear | 1 | E,A,B | 0.500000–0.500000 | 0/4 | 0/4 |
| Linear | 1 | B only | 0.500000–0.500207 | 0/4 | 0/4 |
| Linear | 2 | E,A,B | 1.26e−32–3.77e−32 | 4/4 | 4/4 |
| Linear | 2 | B only | 3.53e−14–0.412325 | 2/4 | 2/4 |
| Tanh | 1 | E,A,B | 0.500204–0.500463 | 0/4 | 0/4 |
| Tanh | 1 | B only | 0.500069–0.524493 | 0/4 | 0/4 |
| Tanh | 2 | E,A,B | 0.000596–0.002030 | 4/4 | 4/4 |
| Tanh | 2 | B only | 0.005516–0.485586 | 1/4 | 0/4 |

All 32 runs completed. There were no nonfinite-run failures or reruns. Eleven runs passed the average-error criterion; ten passed both criteria. These are normalized squared errors, not classification accuracies. Values near 1e−32 reflect floating-point numerical precision rather than exact symbolic equality.

In `linear_d2_readout_s1`, N fell from 1.03768581 to 3.53415e−14 while E and A remained bitwise unchanged in the stored arrays. The sampled minimum singular value rose from 0.0136253 to 0.999999776. Initial and final Jacobian ranks were already two at every sampled context. This is direct evidence of improved use of a fixed hidden representation in this architecture.

In `tanh_d2_readout_s1`, N=0.00551617 passed the average task criterion, but the maximum derivative error was 0.427733, failing the local criterion. Average fit cannot replace a local perturbation audit.

In `tanh_d2_full_s0`, held-out N at step 2,000 was 0.000727119 and at step 3,000 was 0.000793847. The predeclared endpoint remains step 3,000. More updates did not monotonically improve this held-out quantity, although the final run still passed both criteria. Increasing training or parameter count cannot simply be assumed to improve every fixed measure at every step.

## 5. Interventions and what they actually establish

At h1, each final network was evaluated after resetting all coordinates to zero and after separately clamping each coordinate to zero. Future computation used only the remaining two recurrent updates and B. Because this bias-free architecture has phi(0)=0, a complete reset gives y=0 and N=1 in every run. This agrees with the no-bypass implementation; it does not discover an autonomous maintenance mechanism.

For example, in successful `tanh_d2_full_s0`, the two single-coordinate clamps increased N to 0.499817 and 0.500652, respectively; each remaining endpoint Jacobian had rank one at all audit contexts. The clean N was 0.000793847. Both coordinates were needed for the installed two-variable reconstruction at that cut.

The archived `restore` control runs the original, unmodified h1 forward. It reproduces baseline exactly, but is an identity/restoration reference, not an independently implemented damage-and-repair intervention. Its zero difference must not be counted as a separate causal rescue discovery. Setting B to zero independently removes the output while leaving every hidden trajectory unchanged, as expected for a network with no output feedback.

These are explicit interventions on software variables. Clamped states need not lie on the natural input-generated support. No selective physical lesion or organismal result is being claimed.

## 6. Post-result diagnostic: preserve failures, then identify their source

After inspecting the frozen experiment, we declared and ran a separate diagnostic for all eight two-state readout-only networks, including the successes. Ordinary least squares fitted B using the original 25 training examples and the fixed hidden responses; the same held-out grid and derivative contexts were then evaluated. No evaluation target entered the fit. The original Adam runs and their pass counts are unchanged.

All four linear networks then achieved N between 1.06e−31 and 8.63e−30 and passed the local criterion. In particular, the failed Adam seeds 0 and 3 had N=0.0407934 and 0.412325. Their failure was therefore not a proof that the fixed hidden dynamics could not support this task with a linear decoder. It was a limitation of that finite optimization run.

For tanh seed 0, least squares reduced N from 0.0415731 to 0.000219883 and derivative error to 0.0743513. Seeds 1–3 did not receive an analogous remedy: their diagnostic N values were 0.00551629, 0.0455081 and 0.485554, and derivative errors 0.427735, 1.14388 and 1.08020. These are finite-training least-squares fits, not globally optimal held-out nonlinear decoders. Do not infer loss of all information from their remaining errors.

The condition number of the linear seed-3 training representation was 115.574, versus 3.256–8.861 in the other linear seeds. This motivates sensitivity analysis, but does not establish conditioning as the sole cause of the optimizer outcomes: seed 0 failed at condition number 6.111 whereas seed 2 passed at 8.861. No post-hoc training extension or favorable-seed replacement was performed.

## 7. UCT interpretation and relation to the organism–AI question

The relevant A clauses, directly audited in R91, concern actual ports and pointed states, a predeclared continuity topology, C1 and U1. C §5.1 supplies the fixed-evaluation NESIG result. B §5.6 is inherited from the R81 audit, not freshly reread here. No newly discovered A/B/C clause is asserted.

Within C1/U1, valid actual processes have nonempty experience. Whether a process passes this reconstruction task, reports anything, accesses an internal state, or has a biological substrate is not an added existence condition. A claim about AI experiential organization must distinguish this theoretical premise from independently established evidence.

Under a common complete K and a fixed genuine capability functional J that factors through the relevant complete types, equal complete experiential type implies equal J; therefore a genuine J difference implies a complete type difference. The readout-only result respects this implication: B belongs to the actual complete process. It is incorrect both to say “unchanged hidden memory means no experiential change at all” and to infer “large performance gain means equally large experiential gain.” The present finite software task measure is not an exhaustive intelligence functional or a subjective metric.

The constructive contribution is narrower and useful: identify a task-required relation, show its dependence on a declared causal interface, and separate retention from installed use. Merely adding tied copies, stored weights or inactive components does not guarantee such a relation. An operating recurrent computation is not characterized solely by a pile-of-components description either. Neither observation licenses a unified-subject or fear conclusion.

For the inorganic-to-cell-to-animal-to-human comparison, this round supplies a method of specifying organizational differences rather than a new biological result. A cell's maintenance boundaries, animal integration and a model's learned recurrence must be investigated through their actual mechanisms. The delayed-retention network has no metabolism, endogenous viability objective, self/other binding, representation of its own termination or calibrated negative-valence bridge. We must not rename its error or state as fear. Nor does its lack of such modeled features prove absence of every possible experiential feature in its physical execution.

Language expressing fear could similarly depend on an installed input-to-output mapping, on used internal distinctions, or on both. R92 does not test fear words or establish a universal theory of language reports. It shows why report success, representational retention and task use need distinct causal tests. The unresolved organization–valence bridge from R89 remains unresolved.

## 8. Direct precedents and originality judgment

White, Lee and Sompolinsky (2004), *Short-Term Memory in Orthogonal Neural Networks*, analyze recurrent retention and optimal linear readout. Their continuing signal-stream/noise/memory-capacity setting differs from our two simultaneous variables and fixed three updates. Their work is direct prior art for the retention/readout distinction. We read the abstract and the model/readout/memory-function discussion on the first two PDF pages, not the complete article.

Saxe, McClelland and Ganguli (2013 preprint; ICLR 2014), *Exact solutions to the nonlinear dynamics of learning in deep linear neural networks*, analyze factorized linear networks and learning of singular modes. We read the abstract, introduction and initial derivation through the beginning of §1.2. Singular-direction learning is not a new finding of this project. The linear-subspace reconstruction bound is standard geometry; the source ledger also preserves an inaccessible Baldi–Hornik publisher lead without pretending to have read it.

Thus R92 is an actual small experiment and an application that constrains the project's interpretation, not a historical-first theorem, major consciousness breakthrough or empirical verification of C1. Four seeds, synthetic interpolation, restricted decoders, noiseless arithmetic and a short horizon limit its external validity.

## 9. Reproducibility, failures and next step

The package includes the pre-execution protocol, NumPy source, 96,000 training-loss rows, 32 full records with initial/final states and outputs, all interventions, nine checkpoints per run with weights and Adam moments, summary data, gradient/Jacobian checks, diagnostic declaration and results, logs, source scope and hashes. Pre-training maximum gradient-check error was 8.64e−11; final endpoint Jacobian finite-difference maximum error was 7.00e−10. These checks resolve implementation risks, not phenomenal validity. All unsuccessful seeds and the nonmonotonic held-out checkpoint remain included.

Next: use the existing checkpoints and first derive matched clean-task solutions with different state-noise and readout-gain sensitivity at fixed physical ports/units. Separate information retained, information robustly retained and information actually used; do not repeat R79's observer-noise grids or enlarge the models. Only after this identification step specify a minimal self/other future-availability target with actual causal grounding and an independently declared report mapping. No affect label or termination-fear interpretation is licensed by reconstruction performance. R88's comprehension/implementation gates remain pending, and its model-choice experiment remains unrun.

### References

- White, O. L., Lee, D. D., & Sompolinsky, H. (2004). *Physical Review Letters*, 92, 148102. DOI: https://doi.org/10.1103/PhysRevLett.92.148102 . Author preprint: https://arxiv.org/abs/cond-mat/0402452 .
- Saxe, A. M., McClelland, J. L., & Ganguli, S. (2013/2014). *Exact solutions to the nonlinear dynamics of learning in deep linear neural networks*. https://arxiv.org/abs/1312.6120 .
- UCT A v1.2: repository source `research/uct-paper-a-v1-2-20261004:research/uct-paper-a-v1.2/source-template.md`, blob `310204d4e83c5478bf18d34274bcdba996ffda28`; clauses audited in R91.
- UCT C v1: repository source `research/uct-paper-c-v1-20261004:research/unified-consciousness-theory-iii/source-main.md`, blob `fca5d157acb11e5093d617d162d55d4de4fb6961`; §5.1 audited in R91. B audit scope is R81 §5.6, not a new source retrieval.
