# Observable Locality of Constitutive Interventions: A Calibrated Finite-Horizon Gap

**Research:** OL20261009 · **result v0.1.0** · 2026-10-09  
**Parent:** `UCT-MAP-v1.1.0` · **candidate completed map:** `UCT-MAP-v1.1.1`  
**Status:** Proven conditional finite-dimensional results and deterministic executable checks. NOT evidence for phenomenal consciousness, and not a paper/publication approval.

## 1. Scientific question and strict inheritance

The UCT original problem concerns what physically grounded organization contributes to experience, intelligence and self-representation as local processes persist and participate in larger actual systems. UCT I C1/U1/P3 are inherited *conditional theoretical premises*, not proven by the present finite models. Never equate local intervention ability, report, ordinary input–output competence, or the magnitude of a matrix residual with basal experience or with the intensity of a feeling. Neither a unique owner nor a new threshold is proposed.

The preceding completed TH/RB map examined information retained across temporal handoff. The separate pending IL20261009 proved that the complete family of physically primitive one-constituent resets need not be conserved by a generic I/O-equivalent state coordinate change, and constructed a minimal linear-systems witness with a calibrated two-readout max-norm error of 1/11. The pending UI20261009 examined ordered-update noncommutativity. This report does not silently promote IL/UI/R185/AC. The new question is: **given a fixed future observation horizon, a physically stipulated primitive write family, and a calibrated error metric, can we compute the *best attainable* imitation error rather than merely saying the implementations might differ?**

This is operational *reduct* mathematics under a declared experiment. It is not a complete physical-process or phenomenal isomorphism test.

## 2. A precise experiment that separates ordinary behavior from local interventions

Let the recipient have discrete LTI dynamics \(z_{t+1}=Az_t+Bu_t\), \(y_t=Cz_t\), with real \(n\)-state vector. Fix the same initial matched episode, a common future input sequence, and a single instantaneous write at time zero; no later compensating actions before the chosen observations. A source constituent intervention would require a recipient displacement \(v\), determined by the admitted source/recipient chart and the source's *physically installed* write.

The recipient is allowed to modify at most \(k\) nominated primitive components at that same instant, with arbitrary chosen real values and full state knowledge. A subset \(J\subseteq\{1,\ldots,n\}\) has coordinate-injection matrix \(E_J\), so the admissible displacement family is

\[
\mathcal W_k=\bigcup_{|J|\le k}\mathrm{im}(E_J).
\]

For a horizon of \(H\) observations, including the immediate reading, the finite observability matrix is

\[
O_H=\begin{bmatrix}C\\CA\\\vdots\\CA^{H-1}\end{bmatrix}.
\]

Choose a common positive-definite readout precision matrix \(Q\) *before inspecting outcomes*; it can incorporate unit calibration and correlated error conventions. Define

\[
\Gamma_{H,k}(v)=\min_{|J|\le k}\inf_{a}\Vert Q^{1/2}O_H(v-E_Ja)\Vert_2.
\tag{1}
\]

The minimum measures an **operational counterfactual mismatch under a fixed port/horizon contract**, not consciousness quantity. The comparator may optimize the modified component and its value; the experiment does *not* pretend it is restricted to a naive zero-reset only. No hidden synchronized writer is admitted without being included in \(\mathcal W_k\).

## 3. Proposition 1 — Exact optimal observable imitation gap

Let \(W=O_H^\top Q O_H\succeq0\). For any fixed allowed write subset \(J\), denote \(W_J=E_J^\top W E_J\). Then

\[
\Gamma_{H,k}^2(v)=\min_{|J|\le k}
  v^\top\left[W-WE_J W_J^{+}E_J^\top W\right]v,
\tag{2}
\]

where \((\cdot)^+\) is the Moore–Penrose inverse; for \(J=\varnothing\), the subtracted term is zero. If \(O_H\) has full column rank and \(J\ne\varnothing\), \(W_J\) is positive-definite, so an ordinary inverse replaces \(+\).

**Proof.** Set \(D=Q^{1/2}O_H\). At fixed \(J\), minimize \(\|D v-D E_Ja\|_2^2\) by orthogonally projecting \(Dv\) onto the linear subspace \(\mathrm{im}(D E_J)\). The orthogonal projector is \(D E_J(E_J^\top D^\top D E_J)^+E_J^\top D^\top\). Expanding the squared residual gives (2); minimizing over the finite admissible subsets yields the statement. There is no assumed invertibility of \(O_H\) in the general case. This is standard weighted least-squares/projection mathematics, not a newly invented matrix theorem. □

## 4. Proposition 2 — What an exactly zero gap does, and does not, identify

Without a rank assumption, \(\Gamma_{H,k}(v)=0\) iff there exists an admitted write subspace \(J\) with

\[
O_Hv\in\mathrm{im}(O_HE_J).
\tag{3}
\]

If \(O_H\) has full column rank, this is equivalent to \(v\in\mathcal W_k\), i.e. the desired kick is actually k-sparse in the *stipulated installed* primitive components. Thus for full-rank \(O_H\) any \(v\) with more than \(k\) nonzero required physical components has \(\Gamma_{H,k}(v)>0\).

**Proof.** A zero Euclidean weighted residual exists precisely when the desired observation lies in one admitted projected subspace. Since there are finitely many allowed subsets, the infimum is attained by projection. When \(O_H\) is injective, equality of images implies equality of state displacements; otherwise, differences in \(\ker O_H\) can be behaviorally hidden. □

This distinguishes *absence of observable evidence under a short horizon* from *actual availability of a k-local write*.

## 5. Proposition 3 — Bounded-noise rejection of a local organization hypothesis

Suppose both the target and recipient H-traces may each suffer independent **adversarially bounded** readout errors of \(Q\)-norm at most \(\epsilon\). Then whenever

\[
\Gamma_{H,k}(v)>2\epsilon,
\tag{4}
\]

no k-local recipient write can produce an observed H-trace compatible with both noiseless target and mimic, even under their most favorable allowed errors. **Proof.** If they had the same noisy observation, the triangle inequality would make their noiseless discrepancy at most \(2\epsilon\), contradicting (4). □

If \(\Gamma\le2\epsilon\), the single comparison is inconclusive; this does not prove the models are equivalent. No Gaussian significance level, empirical noise floor or brain intervention precision is supplied. The error metric and both noise bounds must be independently calibrated.

## 6. Proposition 4 — Honest coordinate invariance

Under a passive invertible state description \(z=L z'\), transform \(O_H'=O_HL\), \(v'=L^{-1}v\) **and every physically admissible write subspace** \(\mathcal W_k'=L^{-1}\mathcal W_k\), without exchanging it for new coordinate-sparse writes. Then (1) has the same value in either description, because its attainable output difference set is identical.

Failure control: if one redefines “one physical part” as “one coordinate” after a dense passive mixing \(L\), \(\mathcal W_k\) has changed. With \(O=I_2, v=(1,1), k=1\), the squared original gap is 1. For \(L=\left[\begin{smallmatrix}1&1\\1&-1\end{smallmatrix}\right]\), naively selecting k-sparse writes in the new virtual coordinates yields squared gap zero, but this is a **different intervention regime**, not a contradiction of the proposition. This safeguard is especially important for the “slow mechanical brain versus neural network” thought experiment: equivalent descriptions are not new physical supports.

## 7. Concrete two-device counterfactual: a horizon-dependent strict gap

Retain but independently verify the pending IL's exact LTI source and twin:

\[
 A_s=\operatorname{diag}(1/2,1/4),\ B_s=(1,1)^\top,\ C_s=(1,1),\quad
 S=\begin{bmatrix}1&1\\1&-1\end{bmatrix},
\]
\[
 A_r=SA_sS^{-1}=\begin{bmatrix}3/8&1/8\\1/8&3/8\end{bmatrix},\quad
 B_r=(2,0)^\top,\quad C_r=(1,0).
\]

The two devices have identical **ordinary** input–output behavior under matched initial states \(z=Sx\) for any input sequence (induction by linear conjugation). Both LTI realizations are minimal: the source's controllability and observability matrices have full rank and these ranks are preserved by \(S\). Full-state coordinate equivalence is *not* equivalence of the separately declared physically primitive one-component reset operations. By the full local reset-family normal form (product factor permutation plus independent within-factor transformations), their different cross-coordinate dependence excludes any local-reset-preserving dynamics isomorphism; this proof is inherited mathematically from IL's scoped work, reproduced here, **without promoting IL's pending map status**.

**Independent normal-form argument (same explicitly delimited model).** For a Cartesian product of nonsingleton factors and its *complete* primitive reset maps \(R_i^a\), two resets belong to the same factor exactly when their ordered compositions absorb one another: \(R_i^a R_i^b=R_i^a\) and \(R_i^b R_i^a=R_i^b\). Different-factor resets do not satisfy this mutual absorption. A bijective conjugacy preserving the *entire reset family* therefore maps factor families one-to-one. The intertwining equation \(hR_i^a=R_{\pi(i)}^{\phi_i(a)}h\) forces the recipient coordinate \(\pi(i)\) to depend solely on source coordinate \(i\), for all product states and all values \(a\). Thus the bijection is a factor permutation followed by within-factor bijections. Such a map cannot convert autonomous (no cross-coordinate dependence) updates into recipient updates whose first and second coordinates each depend on both current factors; the nonzero \(1/8\) cross terms exhibit that dependence directly. Conversely, missing physical access to a primitive reset or a restricted state support invalidates this full-family classification. The underlying product-automorphism fact is classical; the stated argument is a scoped rederivation, not claimed new algebra.


From \(x=(1,2)\), the recipient has \(z=(3,-1)\) and immediate output 3. A source primitive write \(x_1:=0\) demands a recipient change \(v=(-1,-1)\), giving the source target next two outputs \((2,1/2)\). If the recipient can write any value to one of its primitive coordinates (with complete state knowledge), then:

- At **H=1**, writing recipient \(z_1:=2\) gives the same immediate output, so \(\Gamma_{1,1}=0\). A one-readout test cannot distinguish the specified write mechanisms.
- At **H=2**, optimal weighted \(Q=I\) one-part imitation writes \(z_1:=143/73\) and attains **\(\Gamma^2_{2,1}=1/73\), \(\Gamma_{2,1}=1/\sqrt{73}\)**. Writing only \(z_2\) has a first-readout discrepancy of 1. Neither one-part option attains zero.

For \(z_1:=a\) the two-readout error vector is

\[
\left(a-2,\;\frac{3a-1}{8}-\frac12\right)
=\left(e,\frac{3e+1}{8}\right),\quad e=a-2.
\]

Minimizing \(e^2+(3e+1)^2/64\) gives \(e=-3/73\) and residual squared \(1/73\). The older IL exact max-norm optimum \(1/11\) remains correct under its **different** metric; mixing the two numbers would be a mathematical error. Under two-sided Q-norm error bound, the strict rejection range is \(\epsilon<1/(2\sqrt{73})\).

The result explains how a *temporal* use of a hidden coupling can expose a structural difference that is invisible to immediate performance. Its nonzero gap is a physical-intervention-hypothesis discriminator only if the ports, times and realization are independently established. It is neither a percentage of conscious experience nor a threshold for its existence.

## 8. Failed routes, repairs and application boundaries

1. **First test failure:** the initial projection script used an ordinary inverse for a rank-deficient one-step observation matrix. The correct general statement requires a pseudoinverse, with ordinary inverse only after the rank guard. The executed script has been corrected and retains this failure in the work log.
2. **Countermodel:** rank-deficient \(O_H\) can hide a nonlocal kick. A zero immediate gap does not prove installed locality.
3. **False gauge argument:** dropping the transported write-family condition creates a spurious zero gap after relabeling.
4. **Compensator and hidden-channel control:** a later joint write, a common synchronizer, changed time contract, hidden correlated state or path-dependent readout can suppress the difference; none are automatically excluded by external IQ or a report.
5. **No necessary observable gap for every nonisomorphism:** different constitutive systems can have \(\Gamma=0\) under a weak or incomplete probe family; the method provides a *sufficient refutation of a specified local imitation*, not a complete mechanism identifier.
6. **No experience intensity inference:** the magnitude depends on chosen calibrated units/metric. A small positive physical difference does not establish a large subjective difference or any named quale.
7. **Physical/phenomenal instantiation remains OPEN:** real carrier tokens, actual primitive write loci, complete signature and structural reduct must be independently grounded. Only under these conjunctive premises does inherited C1-OI transfer an independently established full-organizational nonisomorphism to distinct **complete structural types**. It does not prove C1 or a familiar phenomenal feeling.
8. **Local existence conserved conditionally:** actual persisting local processes retain their own nonempty experience under UCT U1/P3; reduced memory or output imitation neither cancels nor guarantees unchanged phenomenal content.

## 9. Executed checks (not biological experiments)

The reproducible Python script `check_observable_locality.py` uses SymPy rational arithmetic and independent NumPy weighted least-squares. Executed with seed 20261009: exact two-horizon twin, the metric-dependent optimum, 1,750 rational-vs-independent numerical projection checks across 630 model/budget configurations, 275 exact passive-coordinate-transport equalities, non-observable and false-gauge counterexamples, and calibrated noise-margin controls. These are finitely scoped checks; the general claims are established by the written proofs, not by finite enumeration alone.

## 10. Primary prior art and claimed increment

- Original UCT I v1.2, UCT II, UCT III and the method MGTD: C1/U1/P3, actual token, fixed common K, theory-target boundaries. Parent map v1.1.0 and pending IL20261009, UI20261009 and R185/AC are provenance, not independent confirmation.
- An established control-systems antecedent is the **observability Gramian** for LTI systems; sensor/actuator selection and Gramian optimization have extensive pre-existing literature. *Efficient Sensor Node Selection for Observability Gramian Optimization*, 2023, PMC10347126.
- *Hankel matrix-based Mahalanobis distance for fault detection robust towards changes in process noise covariance*, IFAC-PapersOnLine 54(7), 2021, DOI 10.1016/j.ifacol.2021.08.337: related weighted fault-detection residuals; not a new invention of the Q metric.
- *Compositional Causal Identification from Imperfect or Disturbing Observations*, 2025, PMCID PMC12294348: local intervention regime antecedent; the present model does not solve causal ontology from observational data.
- *Sparse Actuator Scheduling for Discrete-Time Linear Dynamical Systems*, 2024: sparse actuation and timing known; current use fixes one write instant and a measured horizon, not new general sparse control theory.

**Defensible scientific increment:** an exact, calibrated, physically port-anchored imitation distance and noise threshold that turn IL's binary locality mismatch into a *finite-horizon, optimized, target-relative refutation protocol* tied to UCT's actual-process safeguards. The linear algebra itself is established; novelty of this exact combination and wider experiments have NOT been independently established. Do not announce a new consciousness law or public DOI on this record.

## 11. Formal map integration and governance

This result is a **conditional** addition to the current completed map. The old 1,373-item scientific graph must remain bytewise semantically unchanged. Every new deductive head belongs to a fresh `OL20261009:` namespace, so by induction no new rule can derive a pre-existing head under ordinary positive conjunctive closure. This **syntactic conservativity** does not certify empirical or semantic truth of the old or new premises. Whole-census item checks, cross-family checks, pending-checkpoint exclusion and exact new module status are separately recorded in `MAP_REVIEW_LEDGER.json` and the release audit report. Future results require a new version and matching work log/handoff. All four reviewer-controlled QC obligations remain OPEN.
