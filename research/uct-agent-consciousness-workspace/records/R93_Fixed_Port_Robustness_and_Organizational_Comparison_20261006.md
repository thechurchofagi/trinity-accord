# R93 — Fixed-port robustness and organizational comparison

Research record v1.0, 2026-10-06. Continues R92 at commit `3cc18c1c7c724189e76d5e0def63ece50162369c`. No new training or publication. The user requested a standalone handoff during this round; the bounded analysis below was completed before preparing it.

## Question

Can identical clean reconstruction performance coexist with different responses to the same internal perturbation, without changing state dimension or simply increasing average state amplitude? Yes within the declared linear software implementation family. However, a coordinate change alone does not establish such a difference: the perturbation model must transform with the coordinates. Neither robustness nor amplitude is an experiential magnitude.

## Derivation

Use the R92 linear episode: h0=Ex, h1=Ah0, h2=Ah1, h3=Ah2, y=Bh3. At the h1 cut write M=AE, D=BA², F=DM. Insert an independent zero-mean perturbation e with covariance Q at h1. Then y_e=Fx+De. For any input distribution with finite second moments,

E||y_e−x||² = E||Fx−x||² + tr(DQDᵀ).

The cross term vanishes because e is zero-mean and independent of x. This formula is for the installed downstream map D, not an optimal decoder selected by the analyst. Divide by E||x||² to obtain the normalized R92 error N. Gaussian noise is unnecessary; a finite symmetric pulse distribution suffices.

For an invertible state transformation T, set E'=TE, A'=TAT⁻¹, B'=BT⁻¹. Then M'=TM, D'=DT⁻¹ and F'=F. If the same physical perturbation is redescribed, e'=Te and Q'=TQTᵀ; therefore D'e'=De pointwise and tr(D'Q'D'ᵀ)=tr(DQDᵀ). Keeping Q numerically unchanged after a nonorthogonal transformation specifies a different intervention relative to the state representation. To interpret this as a different implemented causal response, the named numeric registers, additive intervention ports and their units must be fixed. No hardware equivalence follows solely from these software matrices.

### A positive bounded-gain consequence

Suppose M maps d inputs into a state space, D is the installed downstream map, ||DM−I_d||₂≤delta<1 and ||D||₂≤L. For every unit vector v,

1−delta ≤ ||DMv|| ≤ L||Mv||,

so sigma_min(M)≥(1−delta)/L. Thus accurate reconstruction with bounded downstream amplification requires a quantitatively noncollapsed encoding at that cut. It is stronger than rank alone, but conditional on the gain bound, units, norm and uniform/operator-norm accuracy. Average held-out error does not automatically satisfy the premise. For nonlinear systems, only a same-context derivative analogue follows without additional uniform assumptions.

### A matched-state-amplitude consequence

For square invertible M, exact reconstruction DM=I, isotropic input covariance cI_d and isotropic perturbation covariance sigma²I_d, define P=E||Mx||²=c sum_i s_i². Cauchy–Schwarz gives

(sum_i s_i²)(sum_i s_i⁻²)≥d²,

so ||D||F²≥c d²/P and normalized noise error N_noise≥sigma² d/P. Equality requires equal singular values. This is standard matrix geometry, not a new consciousness theorem. P is a squared-state-amplitude budget in fixed numerical units, **not physical energy, metabolic cost, information entropy or phenomenal intensity**. Equal P does not equalize encoder/decoder gain or all implementation resources.

Consider M_epsilon=diag(epsilon,sqrt(2−epsilon²)), A=I, E=M_epsilon, B=M_epsilon⁻¹, for 0<epsilon<sqrt(2). Clean F=I and P=2c for every epsilon. Yet ||D||F²=epsilon⁻²+(2−epsilon²)⁻¹. The same dimension, perfect clean task and matched P leave the noise error unbounded as epsilon tends to zero, unless the downstream gain is bounded. At epsilon=0 the inverse is undefined: this construction does not give a continuous finite-weight path through the singular endpoint.

## Frozen execution and all outcomes

The protocol was declared locally before execution; no independent external preregistration is claimed. The input archive hash was checked against R92's committed package hash. All eight R92 linear two-state runs were included, at both initial and final checkpoints: 16 installed models. No tanh model was transformed with a linear similarity formula. No seeds were added or removed, and no training was run.

The unchanged 64 input pairs have c=0.328125 and E||x||²=0.65625. Four equiprobable pulses ±sqrt(2)*0.01*e_i are evaluated at every input, exactly realizing Q=0.0001 I. This is a deterministic finite-distribution software-state intervention, not measured hardware noise or a Monte Carlo estimate.

For each model, use r=0.25,1,4 and T=a diag(r,1), choosing a to preserve its original P at h1. The resulting 48 transformed cases were executed with clean input, fixed pulses and transported pulses. Each record preserves transformed matrices and all outputs, including failed R92 task models.

All 48 numerical checks passed. Maximum clean-output discrepancy was 1.47e−15; transported-pulse discrepancy 1.55e−15; direct finite error versus covariance-formula discrepancy 2.22e−16; matched-P discrepancy 2.22e−16. Tiny clean-error differences from R92 reflect floating-point multiplication order, not changed task results.

Two final-checkpoint examples, with the full table retained in JSON:

| R92 model | Clean N | Fixed-pulse N at r=0.25 | r=1 | r=4 |
|---|---:|---:|---:|---:|
| linear_d2_full_s0 | 1.70e−32 | 0.00202304 | 0.000461764 | 0.00214821 |
| linear_d2_readout_s1 | 3.53415e−14 | 0.0804508 | 0.00958779 | 0.0175589 |

These are different constructed variants of learned checkpoints, not newly trained networks. The r=1 column is the original implementation. Transporting pulses along with T reproduces the original noisy outputs in every case. No ordering of r is universally optimal; the analysis does not select a new model by test performance.

The separately constructed exact-reconstruction pair at epsilon=1 and0.1 has the same P=0.65625. Their normalized pulse errors are 0.0003047619 and0.0153146686, a ratio of 50.251256. Downstream operator gains are 1 and10. This comparison does **not** fix those gains equal. Both fit a gain ceiling of10; only the first fits a ceiling of1. The 50-fold ratio is an error ratio, not an intelligence or experience ratio.

## Counterexamples and failed shortcuts

1. Scaling all states up by a and inversely scaling the readout reduces error under fixed absolute pulses, but increases P by a². It fails the matched-P control and says nothing about richer experience.
2. Pure coordinate relabeling with transported pulses leaves outputs unchanged. Claiming a structural change from that calculation fails the same-intervention requirement.
3. Setting D=0 eliminates noise transmission but gives N=1 for this task. Low noise sensitivity alone is not better task organization.
4. High inverse gain can recover noiseless inputs from a small-amplitude encoding, yet amplify perturbations. Exact recoverability and reliable installed use differ.
5. The square-inverse budget theorem is not automatically a theorem for redundant/noisy nonlinear encodings, error-correcting architectures or closed-loop maintenance. Those require distinct premises.
6. These interventions are on software states and can leave the natural input-generated support. They are not biological lesions or proof of autonomous self-maintenance.

## UCT interpretation and prior art

Paper A v1.2 §§3.5–3.6 was reread from the preserved published source: actual ports, constituent relations and pointed states must be accounted for; observer-selected probe families and ontic dispositions are distinguished; an invariant topology is additional declared structure. This directly supports the comparison discipline, not the numerical noise model. C §5.1/NESIG and B §5.6 retain their previously audited scope; no new full reread is claimed.

Within conditional C1/U1, actual valid process tokens have nonempty experience without introspection or report gates. A software task description does not exhaust the common complete physical signature K. Equal clean score does not establish equal complete type. If a broader, fixed capability functional genuinely distinguishes actual implementations under specified perturbations and meets the C1/NESIG factoring premises, complete experiential types must differ. The numerical magnitude and direction of experiential richness, unity or negative valence still do not follow. No arbitrary different experience is assigned to an identical complete organization.

The formulas here belong to standard linear systems, estimation and matrix inequalities. Sanjay Lall's Stanford EE263 *The linear model* slides were read through the covariance, gain and posterior-error discussion (PDF pages1–11). They supply direct background for covariance propagation and the difference between inversion and estimation. Moore (1981), *Principal component analysis in linear systems: Controllability, observability, and model reduction*, was located as a close control-theory precedent, but its PDF fetch timed out; only search metadata/abstract snippets were available. A follow-up search returned irrelevant results. No detailed theorem is attributed to unread text, and no exhaustive novelty clearance is claimed.

R77 already establishes that coordinate transformations must preserve intervention relations, and R79 already distinguishes specified robustness from complete experience. R93 adds the matched-amplitude/noise-transport control and actual replay of R92 checkpoints; it does not claim a historical-first robustness theorem, major consciousness breakthrough or subjective measurement.

## Handoff conclusion and next step

This small analysis is closed: do not expand its noise grid or train bigger models to manufacture progress. Return to the user's main question with a minimal predictive task in which world-state information and the current process's future availability have separately specified causal consequences. First derive which distinctions prediction requires, then distinguish those retained distinctions from the installed report map. A future-availability variable must be causally grounded and distinguished from task completion, successor continuation and language labels. Do not call a scalar error, robustness improvement or self-specific control preference fear. R89's valence bridge and R88's comprehension/implementation gates remain unresolved.

Reproduction: `python r93_state_noise.py > R93_Run.log` in an extracted copy; requires NumPy. Outputs are overwritten only in that copy. `R93_Inputs.json` contains all selected-by-design initial/final weights; `R93_Results.json` has every summary and the constructed-pair pulse outputs; `R93_All_Pulse_Outputs.json` has every transformed-case output; no original R92 file is changed.

Primary teaching source: https://ee263.stanford.edu/lectures/linear_model.pdf . Prior-art lead with retrieval failure: https://doi.org/10.1109/TAC.1981.1102568 . All source scope and failures are separately logged.
