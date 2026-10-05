# R92 frozen protocol — learned delayed retention at a fixed causal cut

Version 1.0, 2026-10-06. Written before any training. Continues R91 at commit b7216371757da38eb12af873bba864fc4f9123ca.

## Question and derivation before execution

Can an installed tiny network learn to retain and jointly reconstruct two independently varied inputs after those inputs are removed? Does improvement require new state dimensions, or can it improve use of dimensions already present? This is an organization/capability question. No coordinate is assigned fear, selfhood or hedonic meaning.

Model: h0=phi(E x); ht=phi(A h[t-1]) for t=1,2,3; y=B h3. Phi is either identity or tanh. No biases, skip connections, later input, output history or residual bypass. Fixed software bearer includes encoding, three recurrent updates and installed decoder. Dimension d in {1,2}; total weights 4d+d² (5 or 12). External supervisor/optimizer is outside each frozen inference episode.

For d=1, every output lies in the at-most-one-dimensional image of the linear B. For a zero-mean isotropic two-dimensional evaluation distribution, normalized squared reconstruction error N=E||y-x||²/E||x||² is at least 1/2, regardless of nonlinear hidden transformations. This is a decoder-subspace bound, not a universal nonlinear scalar-memory bound. For linear d=2, E=A=B=I can attain zero error, so the task is feasible. Nonlinear training convergence is not guaranteed.

For both activation families, the differential endpoint map factors through the same d-state bottleneck. Its local Jacobian has rank at most d. The criterion ||Dy-I||2<0.2 at a stated context implies sigma_min(Dy)>0.8 and two retained/used local directions there. Finite context sampling is not a certificate throughout a continuum.

## Data and training

Training inputs: all 25 pairs in {-1,-0.5,0,0.5,1}², target=x. Evaluation: all 64 pairs in {-0.875,-0.625,-0.375,-0.125,0.125,0.375,0.625,0.875}²; none occur in training. Both grids have isotropic covariance. Audit contexts: {-0.75,0,0.75}². This is synthetic interpolation, not real-world generalization.

Four seeds 0,1,2,3, both dimensions, both activations, and full-training/readout-only conditions: 32 runs. Initial weights from NumPy default_rng(seed): E=0.3*N(0,1), A=0.9I+0.05*N(0,1), B=0.3*N(0,1), in that order. Same initialization is reused for paired full/readout-only runs of each activation/dimension/seed. All runs use 3000 full-batch Adam updates on plain mean squared output error, learning rate 0.01, beta1=0.9, beta2=0.999, epsilon=1e-8; global gradient norm clipped at 10. No internal-state, Jacobian, rank or affect objective. No weight decay, restarts, seed replacement, step extension, learning-rate schedule or model selection.

Readout-only trains B with E,A exactly frozen. Full training changes all three. Checkpoints at 0,10,50,100,250,500,1000,2000,3000, with all weights and optimizer state. Record loss every update. Stop only a numerically nonfinite run and preserve its failure; continue remaining runs unchanged. Use float64 on CPU.

## Outcomes and interventions

Primary task threshold: held-out normalized error <0.01. Separate local certificate: maximum ||Dy-I||2 over all nine audit contexts <0.2. Report each threshold and their conjunction without tuning. Retain all initial/final outputs, state trajectories, sampled Jacobians, singular values, checkpoint weights and losses.

At final weights, intervene on h1, after one recurrent update: reset all state coordinates to zero; separately clamp each single coordinate to zero; restore original h1 and compare with baseline. Continue with two recurrent updates and B, never reread x. These are explicit software-state interventions, not claims about naturally occurring hidden states. Retain all held-out outputs and local Jacobians for each condition. Independently remove B (zero output), which must preserve h0..h3. These controls distinguish retained information from installed use and exclude an accidental input bypass.

Before training: check analytic gradients against central differences at the first initialization of both dimensions/activations (step 1e-6; maximum absolute deviation <1e-6). After training: check analytic endpoint Jacobians against central differences at the nine contexts for each final model (step 1e-6; maximum absolute deviation <1e-6). These address real implementation risks. A code failure must be logged and repaired without quietly changing the scientific protocol.

## Scope

Rank and singular values are finite software descriptors with fixed units/coordinates, not phenomenal measures. A readout-only improvement changes the complete inference implementation through B even if hidden memory is exactly unchanged; it does not contradict conditional NESIG. One-state failures cannot exclude arbitrary nonlinear decoding, packed finite codes or external memory. Two-state success need not add a new initially absent dimension or prove autonomous maintenance, unified subjecthood, world understanding or fear. C1 interpretation requires actual valid tokens and a common complete K; no introspection or report existence gate is imposed. Published A/B/C and the integrated manuscript remain unchanged.
