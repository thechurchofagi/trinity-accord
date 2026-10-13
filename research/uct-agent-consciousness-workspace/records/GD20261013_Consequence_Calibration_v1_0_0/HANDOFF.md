# UCT-GD-2026-01 v1.0.0 — prepared preprint handoff

Date: 13 October 2026. Human author: Hongju Liu, independent researcher, Shenzhen, China. Substantial derivation, code, execution, review and drafting assistance: ChatGPT / GPT-6 Astra Pro.

## Manuscript and exact status

**Learning What to Preserve Without Silencing the Body: Adaptive Organization, Mutable Evaluation, and Reference-Calibrated Regulation.** English theoretical/computational preprint, 18 pages, 15 references. New integrated work consolidating GD v0.1–v0.3 and adding a mutable-evaluator calibration layer. Not independently peer reviewed; global priority not certified. No new DOI was reserved, submitted or published; no OTS or Arweave operation. No prior paper or archive amended. No requested CI or PR.

The user requested continued research until a work is ready for DOI, not an automatic publication transaction. The prepared metadata remains a proposal. The completed UCT map remains UCT-MAP-v1.1.2; the entire historical semantic map was not freshly re-audited. GD18–GD24 stay disabled as automatic UCT premises. The guide and current research branch were read; the main catalog still gives its older check date and is not treated as a fully current publication audit.

**Persistence boundary:** This directory contains a substantive research handoff and, when its following upload is confirmed, the core reconstruction code. It is NOT the complete PDF, manuscript, raw study files or predecessor archives. Complete artifacts are downloadable in the originating conversation. Obtain and hash-check them rather than reconstruct missing files from this summary. A remote handoff is not a full backup.

## Why this now forms one scoped paper

GD0.1 studied retention under selective communication; GD0.2 installed a bodily feedback loop; GD0.3 let paired probes learn a routing from binary consequences but assumed an invariant evaluator. The new layer permits evaluator gain and background to change with the organization, recovers a physical deviation under explicit shared-reference conditions, and retains exact cases where that recovery fails. This is one mechanism/identification problem with proofs, bounds, experiments and falsifying cases, not another standalone copying example.

This is not a first-self or consciousness-onset theory. Basal experience is not identified with successful regulation, a reference signal or an alarm. The finite model does not establish complete ontic organization or a named phenomenal quality. The origin/maintenance of the reference architecture remains an additional problem. Both actual improvement and sensor suppression can be gradual.

## Inherited regulator, explicitly scoped

For p in [0,1], two compartments mix signals through P(p)=1/2 [[1+p,1-p],[1-p,1+p]]. Common signals pass; differential signals attenuate. Passive physical coupling remains at p=1. In the difference sector:

 dz=(-a z-k w)dt+sqrt(2D)dW;
 dw=(b p z-b w)dt+sqrt(2 b^2(Np^2+M))dV.

The fixed-p Gaussian body variance is

 V(p)=D/(a+b)+b/(a+b)*(D+k^2(Np^2+M))/(a+kp).

a,b,k,D>0, N,M>=0. N enters before mixing; M after. At p=1 the N/M twins with equal sum have the same full observed process law, but intervention effects differ. The generic optimum is clip((sqrt(a^2+(D+k^2 M)/N)-a)/k,0,1) for N>0; N=0 gives p=1. The sensory-activity objective with M=0 strictly favors p=0, which need not improve body regulation. These are inherited GD results, not newly novel merely by inclusion here.

## New GD18–GD24 core

Let X be a centered Gaussian body of known dimension n and covariance Sigma. The binary monitor's no-alarm probability is s exp(-r ||X||^2). Sensitivity r>0 and background factor 0<s<=1 can change across organizational settings. During one held-setting block, the relevant gain, background and bodily distribution are fixed. A zero and a nonzero reference squared input C enter the same consequential input path. The calibration monitor is separate from the regulator's continuously used sensing channel; reference probes must not silently substitute test inputs into the body's control loop.

### GD18: scale ambiguity

Body readings at any known relative gain t satisfy q(t)=s/det(I+2tr Sigma)^(1/2). Replacing Sigma by c Sigma and r by r/c preserves every such probability. Scaling the whole Gaussian body path and coupling comparator randomness preserves the entire declared alarm history. Thus uncalibrated relative-gain sweeps do not fix an independently changing bodily scale. This is an explicit observation-family ambiguity, not a universal claim about every sensor.

### GD19: four modes recover a two-dimensional trace

q0=s; qC=s exp(-rC); q1=s/det(I+2r Sigma)^(1/2); q2=s/det(I+4r Sigma)^(1/2).

r=log(q0/qC)/C; F1=(q0/q1)^2; F2=(q0/q2)^2.

 trace(Sigma)=(4F1-F2-3)/(4r);
 det(Sigma)=(F2-2F1+1)/(8r^2).

Proof: the determinant polynomial in two dimensions is 1+2tr trace(Sigma)+4t^2r^2 det(Sigma); solve its values at t=1,2. No preferred eigenbasis or plant parameters are given to the reconstruction. Four MODES require repeated samples to estimate four probabilities, not four bits. An unknown fixed actual reference scale returns a fixed positive multiple and preserves rankings. A changing reference scale does not.

When exact factor-two gain/common background is unavailable, separately calibrate two distinct gains with zero/reference/body in each (six modes). With Bi=((q0i/qbi)^2-1)/(2ri), trace=(r2 B1-r1 B2)/(r2-r1). Same path and same body distribution remain required.

### GD20: finite-dimensional query frontier

For known n, F(t)=(s/q(t))^2=det(I+2tr Sigma) has degree at most n and F(0)=1. n distinct positive gain points suffice to recover F'(0)=2r trace(Sigma). At integer gains j=1..n:

 trace=[-H_n+sum_j (-1)^(j+1) binom(n,j) F(j)/j]/(2r).

Fewer m<n predetermined positive body gains cannot universally recover trace over all positive-definite covariances: perturb a polynomial with distinct simple negative roots by epsilon*t*product_j(t-t_j). Queried values and F(0) stay fixed, F'(0) changes, and sufficiently small real epsilon preserves simple negative real roots and hence valid positive eigenvalues. This is classical interpolation/root continuity in a specific application, not a lower bound on all measurement designs, bits or computation. An explicit n=2 one-gain pair is eigenvalues (1,1) versus (.5,5/3) at r=.5; F(1)=4 but traces differ.

### GD21: the reference can test the wrong path

If body readings use rB but references calibrate rC, reconstruction returns (rB/rC)*trace(Sigma). Quadruple bodily variance and reduce only body-input squared gain by four: all four readings remain unchanged, including functioning references. This is the retained bypass counterexample. Independent ratio bounds give corresponding trace bounds. Mode interleaving is not a proof against arbitrary mode-dependent tampering.

### GD22: finite precision and abstention

Given simultaneous q intervals [l,u], positive endpoints and l0>uC, rL=log(l0/uC)/C and rU=log(u0/lC)/C. Fj ranges between (l0/uj)^2 and (u0/lj)^2. The numerator 4F1-F2-3 and denominator 4r yield a conservative interval using endpoint combinations. Negative-upper contradictory trace intervals are rejected. Gain not separated from zero returns NO_SCORE, not zero bodily cost.

Exact binomial intervals require independent trials; selection across K settings requires all 4K mode intervals or another valid simultaneous guarantee. Correlated/adaptive records are not IID merely because comparator coins are fresh. At r=0 all body information is absent. Near zero no fixed finite read budget distinguishes covariances uniformly. The stated O(r^2) local divergence illustration assumes 0<s<1, not the s=1 boundary.

For stationary Gaussian joint states at lag tau, Sigma_tau=[[Sigma,Ctau],[Ctau^T,Sigma]], covariance of two distinct no-alarm bits is s^2*(det(I+2r Sigma_tau)^(-1/2)-det(I+2r Sigma)^(-1)). The variance of their average includes the full lag-covariance sum.

### GD23: exact non-Gaussian twin and positive alternative

At r=1, Gaussian Sigma=I/2 has E[U]=1/2 and E[U^2]=1/3 for U=exp(-||X||^2). Put epsilon=.001 probability on U=d in (0,1/16] and remaining probabilities on .1,.5,.9:

 w1=(4973+84d-60d^2)/19200;
 w2=(23027-300d+300d^2)/48000;
 w3=(4997+36d-60d^2)/19200.

These are positive, sum with epsilon to one, and exactly preserve both U moments. A uniform independent angle makes X centered. Its mean squared deviation includes -epsilon log d and is unbounded as d approaches zero. All four monitor probabilities and elementary Gaussian consistency checks pass. Calibration readings cannot certify Gaussianity.

If an independent physical bound E[E^2]<=M2 holds for E=||X||^2, define L=(1-qbody/q0)/r. Elementary exponential inequalities give L<=E[E]<=L+r M2/2 without Gaussianity. A known E<=B yields upper bound rB L/(1-exp(-rB)). A smaller gain reduces this truncation gap but increases sampling difficulty. The physical moment bound is not supplied by the same four readings.

### GD24: actual finite sample result

21 candidate p values, 32 seeds per environment, 65,536 independent stationary draws per mode; r(p)=.2+1.8p^2, s(p)=.85-.1p. Selector sees only settings, empirical four-mode fractions, C and known factor two; not r/s functions, plant parameters, body values or optimum. Raw selector minimizes alarm; calibrated selector minimizes recovered trace. Final values are evaluated from the selected setting's physical model, not the noisy winning score.

Median differential variances: upstream raw .4181818 vs calibrated .3636364; downstream 2.9025974 vs .8787879; low upstream 3.0525325 vs 1.2196970. Calibrated is better in all 32 seeds in each of these three recorded environments. No universal dominance, efficiency or safety claim. Exploration cost is not included.

This finite selection study has independently prepared stationary samples. The predecessor online carried-state learner has fixed monitor calibration. Their fully online, mutable-evaluator, confidence-certified combination is NOT implemented here and remains open.

## Actual verification and scope

Three new scripts were run twice, all five primary JSON/CSV outputs byte-identical. GD v0.3's entire learner/verifier was rerun and six primary files matched originals. New checks include 80 rational 2D identities; 24 rational n-dimensional checks; 1000 rotated covariances; 1000 deterministic enclosures; five fewer-gain witnesses; five exact non-Gaussian witnesses; 400 six-mode checks; 1000 moment-bound cases; 90 regulator Lyapunov checks. All assertions passed. General claims rely on printed proofs, not enumeration.

Precision study: seven gains, 1000 IID trials each. At r=.0001 and .001 all returned no score. At .01 467/1000 returned no score; remaining intervals were very broad. The separate 128-read stationary temporal example has analytic variance .00311870 vs IID .00181175, a factor 1.72137; 16000-record Monte Carlo gave .00314923.

The final PDF was rendered, all 18 pages inspected, key equations/tables viewed at page size. Fonts embedded, no overfull boxes. Internal AI-assisted work is not independent peer review. A near-final accidental 'only while calibration is fixed' necessity statement was weakened to its actually proved sufficiency statement.

## Closest predecessors

UCT C1/U1 and fine-chain context are inherited. REGI spatial averaging/noise tradeoffs (Mugler et al. 2016), homeostatic RL (Keramati & Gutkin 2014), reward tampering (Everitt et al. 2021), extremum seeking, one-bit/dithered covariance recovery (Dirksen et al. 2022; Dirksen & Maly 2024), self-calibrating sensors, Gaussian transforms and polynomial interpolation are credited. Source access is targeted, not a systematic/global novelty certificate. This is not a new proof of panexperientialism, a canonical subject selector, or identification of a named phenomenal target.

## Final artifact SHA-256 identities

- manuscript.md: 55,362 bytes; 811daccd587da4a7ebc429a36bc130400f3e651acda799b5e7dd4d8d2c111cad
- Learning_What_to_Preserve_v1.0.0.pdf: 387,107 bytes; 7ab1d84f93d194f3cde694bfb6f7e8bacaae5547b88afdac9aba886f1c602df4
- code/calibration_core.py: 2,654 bytes; f2e87741a0ccade88105d7fc855e6697854185a8a8e89c4eb932c59155fbd710
- results/PROOF_CHECKS.json: 3,145 bytes; 28b0225d2481c6188a278d8648d5950210e6eb0e13569c9e2daac688fda44f6d
- review/FINAL_SCIENTIFIC_REVIEW.md: 9,606 bytes; df2f074f15987b1cc9e7173a069dd6b3c0efc4af054634a02a374d45f07ba157

Originating local folder: /mnt/data/Adaptive_Consequence_Calibration_v1.0.0. Local paths are not permanent public URLs. Downloadable preprint/package filenames are recorded in the conversation. Retrieve actual files before deposition.

## Next publication step

Review the proposed author/rights metadata and freeze actual deposition bytes. If subsequently authorized, create a new preprint record, never overwrite prior works. Any real DOI insertion precedes final byte freeze and review. Verify published file readback anonymously, then OTS/Bitcoin, then guarded Arweave under the repository per-edition strict .1 AR budget and other safeguards. Do not increase publication counts, promote the map, or invent receipts from this prepared status.
