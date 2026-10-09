# When Successful Compensation Hides Organizational Change

CM20261009 / CM-RESULT-v0.1.0, 9 October 2026. Candidate theoretical research, not peer reviewed or a published paper. Method: MGTD and highest guide v2.1. Parent completed map: UCT-MAP-v1.1.1; source head read 2fb510071b34c1df434e1ef7cd6d853051ce7907. New module stays PENDING_MAP / AUDIT_INCOMPLETE, disabled as established premises.

## 1. Question and strict inheritance

OL's finite-horizon locality gap excludes later corrective actions; R186 concerns hidden interactions invisible to all short reset sequences. Here we instead allow active compensation. R177/IE already preserve behavior through inverse-compensated recoding; EI/CORE already address bypasses and target-relative necessity. Those are inherited, not new discoveries. The question is what a quiet outcome tells us when another part actively offsets a change, and what limited correction observation can identify the masked target.

UCT C1/U1/P3 are unchanged. A persisting local actual process retains nonempty experience; quiet output, poor performance, monitor success or correction magnitude neither cancels experience nor measures a named feeling. Actual participation in the original episode is not established solely by hypothetical intervention sensitivity.

## 2. Fixed model and causal interpretation

Fix preparation, interval, target, units, permitted ports and timing. In real finite-dimensional coordinates let

    e = d + M u,    z = H u,    q = K d.                 (1)

Here e is an outcome contrast, u is the complete admitted change of corrective action, M its independently calibrated influence, H a correction monitor, and K a selected-target projection. K in these formulas is NOT UCT's full constitutive signature. The target and matrices are fixed before looking at results.

The meaning of d as the effect with correction held at baseline needs an independently justified modular/clamp model. Without that, e-Mu is just an algebraic residual, not a newly discovered cause. Omitted correction inputs, changing M or nonlinear interactions require additional modeled terms and bounds. External clamp apparatus belongs to the causal boundary. For the necessity theorems, d and u range freely over their declared real spaces; restricting physiologically feasible pairs may invalidate necessity, although a valid reconstruction remains sufficient. No algebraic cancellation is assumed causally available before its inputs arrive.

## 3. Causal recovery witness

For scalar constant d, e_t=d+u_t is read BEFORE u_(t+1)=u_t-alpha*e_t, u_0=0, 0<alpha<=1. Induction gives

    e_t=d(1-alpha)^t; u_t=-d[1-(1-alpha)^t].              (2)

With alpha=1, all readings from t=1 onward equal zero even for d=1, while correction remains -1. With alpha=1/2, readings go 1,1/2,1/4,...; in every case e_t-u_t=d. The original t=0 transient distinguishes the perturbation. Late output agreement is NOT full-trajectory agreement, and extending late-only observation may never settle the ambiguity. This differs from R186's insufficient excitation-depth example.

## 4. Exact target-identification theorem

In the unrestricted exact class (1), q is determined by (e,z) for every (d,u) iff

    ker(H) is contained in ker(KM),

or equivalently row(KM) is contained in row(H), or KM=LH for some L. Then

    q = K e - L z.                                     (3)

Proof of sufficiency: substitute (1). Necessity: if v is in ker(H) but KMv is nonzero, (d,u)=(0,0) and (-Mv,v) give the same (e,z)=(0,0) and distinct q. No nonlinear decoder can distinguish them. Row/null-space duality supplies the equivalences.

If freely designable, noiseless, ideal real-valued linear monitors are admitted, the minimum number of independent monitor channels is rank(KM): row containment is necessary and a row basis is sufficient. This is not a bit-count, anatomical-region, energy or experiential-complexity bound, and an actual monitor's implementability remains separate.

Concrete witness: M=[1 1], K=1, and either Hplus=[1 1] or Hminus=[1 -1]. Both return one number. Hplus gives d=e-z. Under Hminus, d=1 and u=(-1/2,-1/2) are observationally identical to d=0,u=(0,0). Measuring some correction activity is not necessarily measuring the target-relevant combination.

## 5. Sharp bounded ambiguity theorem

Add ||u||_2<=rho and leave d unrestricted. For feasible exact z, set

    u0=H^+z; P=I-H^+H; s=sqrt(rho^2-||u0||_2^2).

Feasibility means z in im(H) and ||u0||<=rho. The exact feasible target set is

    {K e-KM u0-KM v : v in ker(H), ||v||<=s}.            (4)

Among all estimators of q from these observations, the exact conditional minimax Euclidean error is

    R(e,z)=s ||KM P||_2,                                 (5)

attained by qhat=K e-KM u0. The norm on matrices is spectral. Uniformly over feasible z the worst radius is rho||KMP||_2, attained at z=0.

Proof: every compatible u is u0+v with v in ker(H); the two terms are orthogonal, giving the residual-radius ball in (4). Its linear image is centrally symmetric. Its farthest radius is (5); antipodal extremal singular-vector points are 2R apart, so no estimator improves the worst case. Centering attains it. Zero-radius cases follow directly. Additional constraints on d can reduce the set: equality is NOT asserted after introducing those constraints.

For the two-monitor witness with rho=1/sqrt(2), z=0, the ambiguity radius is zero under Hplus but one under Hminus. In the latter case all d in [-1,1] can fit the same e=z=0. A full target-relevant correction record is unnecessary, but losing one relevant direction can matter exactly.

Passive changes of correction coordinates must transport M, H and the correction ellipsoid together. Reimposing a fresh Euclidean budget after mixing coordinates is a different physical experiment, not a failure of invariance.

## 6. Error, budget and timing guards

From (1), ||u||<=rho and ||e||<=epsilon imply ||d||<=epsilon+||M||rho. The scalar M=1 minimal residual is max(0,|d|-rho). This is a triangle bound, not a thermodynamic or phenomenal law.

For e=d+Mu+w, ||w||<=epsilon_m, noisy readings within epsilon_e and epsilon_z, and KM=LH,

    ||K e_measured-L z_measured-Kd||
      <= ||K||(epsilon_e+epsilon_m)+||L||epsilon_z.        (6)

No statistical independence of these bounded errors is needed, but the bounds and the causal decomposition need independent support.

Complementary timing lemma: in a protected window let e=G xi+b, where xi is mean zero, has nonsingular covariance Sigma, and is independent of all information available to the compensator before the scored readout; b is measurable from that prior information with finite second moments. Then

    E[e xi^T]=G Sigma;
    E||Q^.5 e||^2=tr(Q G Sigma G^T)+E||Q^.5 b||^2.        (7)

Proof: independence eliminates the cross terms. These are population identities, not sample-level significance guarantees. If the compensator sees the current xi it can choose b=-Gxi; the result no longer applies. No human latency value or intervention protocol is proposed. Hidden contemporary inputs, predictable probes or apparatus that knows the probe must not be ignored.

## 7. UCT application boundary

Maintained behavior can reflect low target relevance, redundancy, compensated recoding or active regulation. These are distinct organizational possibilities; none is a test of whether experience exists. Under independently established actual tokens, shared full signature/ports/timing, and an invariant reduct difference, inherited C1-OI yields different complete experiential structural types. It does not give a named feeling, intensity, subject count or current-assistant verdict. Applying C:P1 requires the same true capability J, including policy/resources, not just a changed realized correction trace. Actual original-episode participation still requires occurrence evidence. Local physical persistence must satisfy P3, rather than being inferred from a saved label.

## 8. Prior art, validation and readiness

Unknown-input observers, set-membership estimation, effect-relevant sufficient statistics and randomized excitation are established. Close primary antecedents: Tranninger, Niederwieser, Seeber and Horn (2023), DOI 10.1002/rnc.6399; Meslem, Hably and Raissi (2023), DOI 10.1177/09596518231153316; Jesse, Sun and Hwang (2022), arXiv:2210.10927; Wang et al. (2020), DOI 10.1002/rnc.5036. Publisher abstract/method overview access is NOT exhaustive theorem-level originality clearance.

Motor adaptation and error-clamp studies by Smith, Ghazizadeh and Shadmehr (2006), DOI 10.1371/journal.pbio.0040179, and Ethier, Zee and Shadmehr (2008), DOI 10.1152/jn.00015.2008, motivate distinguishing outward recovery from hidden organization. No raw data reanalysis or claim that those experiments validate equation (1) or C1 is made.

Expanded local checker actually passed 1,296 matrix contracts, 730 nullspace counterwitnesses, 566 reconstructions, 1,296 bounded-radius cases, 1,460 antipodal endpoints, 216 variable-dimension cases, 99 feedback rows, 75 latency-moment cases and 153 scalar budgets. The separate compact core_check.py was also run successfully; it reproduces the principal exact claims, not all expanded cases. No biological or actual LLM subjective experiment occurred.

Defensible contribution: a target-specific active-compensation extension with a sharp ambiguity formula, a same-observation-size contrast and causal timing alternatives. It is candidate paper material, not an important new consciousness law established by these tests. Full priority comparison and current-map integration remain prerequisites to promotion; no publication/DOI/OTS/AR or scheduler action.

## 9. Map and preservation

MAP_EXTENSION.json carries 24 nodes, ten conditional rules and four non-deductive links. New IDs/AND premises/acyclicity and local proof limits checked. Current completed release v1.1.1 has 1,419 records. Their complete ID ledger and historical v1.0.0 source were available; 18 related inherited clauses were reread. The complete v1.1.1 binary capsule could not be downloaded. Hence full fresh itemwise semantic integration is NOT claimed, R186's 625 obligations are NOT discharged, and CM stays disabled PENDING_MAP / AUDIT_INCOMPLETE. The official current version must not be incremented by this checkpoint.

This compact remote checkpoint preserves all displayed proofs and scope conditions. The downloadable local package additionally contains the longer manuscript, expanded checker/results, historical sources, per-ID incomplete-coverage inventory and paper-readiness assessment; they are not byte-identical serializations. Read WORK_LOG.md, HANDOFF_ZH.md and PERSISTENCE_RECEIPT.json before resuming.
