# GD v0.3.0 — Learning What to Preserve Without Silencing the Body

Date: 2026-10-13. Human research direction: Hongju Liu. Substantial derivation, code, execution and review: ChatGPT / GPT-6 Astra Pro.

## Persistence and scientific status

This is a substantive research checkpoint, not a new paper or DOI. The full local package is `UCT_Gradual_Differentiation_Research_v0.3.0.zip` in the originating conversation. This GitHub directory preserves a detailed scientific handoff, exact numerical summaries, candidate scope and artifact fingerprints. IT IS NOT A FULL MIRROR OF THE SOURCE CODE, FULL RESEARCH NOTE OR RAW TRAJECTORIES. Obtain the actual downloadable package for full reproduction. Do not reconstruct missing files from this summary or claim they were uploaded. No DOI/OTS/Arweave operation, no PR, no requested CI run, no change to published papers.

The prior v0.2.0 package was read and its original verifier rerun; its three primary result files matched the supplied bytes. The current guide and current-state scope were checked. Authoritative map remains UCT-MAP-v1.1.2, and the all-history semantic audit remains incomplete. GD13–GD17 are disabled candidate claims, not new accepted empirical UCT premises. A5L's coordinate-to-selected-experience barrier remains open.

## What was actually advanced

GD0.2 let an analyst choose a good regulatory routing. This round installs paired-probe learning that receives only binary alarms about total deviation of two physical compartments. It is not given noise-source identity, physical parameters, the variance formula, an optimal setting, body/regulator states, or a target difference-coordinate score. The same learner develops different routing in the two history-matched mechanisms. A control using sensory-regulator alarms learns to suppress the sensing channel instead, worsening actual bodily regulation in a low-noise regime.

The evaluator, reference states, adjustable port and algorithm are installed assumptions. Only a routing strength is learned. This is not evolution of the entire architecture, natural selection, a human/animal experiment, subjective pain measurement, evidence of a first self, or proof that a particular controller variable is felt ownership.

## Inherited plant

Two compartments use P(p)=1/2 [[1+p,1-p],[1-p,1+p]], p in [0,1]. Lower p mixes their sensory signals more. Physical body coupling remains at p=1. In a fixed orthogonal basis the differential sector is

 dz=(-a z-k w)dt+sqrt(2D)dW;
 dw=(b p z-b w)dt+sqrt(2 b^2(N p^2+M))dV.

N enters before mixing, M after. a,b,k,D>0 and N,M>=0. Its stationary body variance is

 V(p)=D/(a+b)+b/(a+b)*(D+k^2(Np^2+M))/(a+kp).

The common sector is always p+=1 with a+=.1,b=2,k=1,D+=.1,N+=.01,M+=0. Common body variance is 1/7. The full simulation has four states. Independence of sectors is used at fixed p, not asserted during adaptation through a common monitor.

## GD13: a strict sensory-muting result

For M=0 set A=D+a(a+b)N>0 and B=bkN>=0. The regulator variance is

 T(p)=b p^2(A+Bp)/[(a+b)(a+kp)].

Its derivative is b p[2aA+(kA+3aB)p+2kBp^2]/[(a+b)(a+kp)^2], strictly positive for p>0. Thus minimizing sensory variance, or any fixed strictly increasing function of it, favors p=0. Adding the unchanged common sensory variance does not repair this.

For a=.2,b=2,k=1,D=1,N=.01,M=0, actual bodily regulation is best at p=1 with differential variance 1.21969697; p=0 gives 5. A lower internal signal is not itself a better regulated body. This is a precise application of an established reward-input/evaluation problem, not the first discovery of wireheading or a claim of deception.

## GD14: body calibration and its counterlimit

At sampling times an installed binary monitor has P(alarm=1|x)=1-exp[-r(x1^2+x2^2)], r>0, with independent comparator randomness. The learner sees only the alarms. For fixed p:

 J(p)=1-[(1+2rV+)(1+2rV(p))]^(-1/2).

This is strictly increasing in V(p). Unknown fixed r changes statistical sensitivity but not the optimum. More generally, a fixed increasing function of total squared body deviation preserves the ordering by coupling the same Gaussian common and difference inputs and scaling only the latter. Strictness and finite expectations need their stated conditions.

The premise is physical calibration, not the word 'intrinsic'. If the adjustable gate can instead set r(p)=r0 p^2, J(0)=0 regardless of the worsened body. A separately fixed monitor is one sufficient construction, not a universal necessity for agency or consciousness.

## GD15: finite-probe target and conditional convergence

Let C=D+k^2M+a^2N. The symmetric variance comparison is exactly

 [V(p+d)-V(p-d)]/(2d)=bk/(a+b)*[N-C/((a+kp)^2-k^2d^2)].

Every strictly increasing J=H(V) gives the same comparison sign and zero. For N>0 the unprojected root is p_d=(sqrt(C/N+k^2d^2)-a)/k. Clip to [d,1-d] for a fixed symmetric-probe domain. N=0 gives the upper endpoint. An interior root differs from p* by k d^2/[sqrt(C/N+k^2d^2)+sqrt(C/N)].

The tangent-projected ideal stationary-mean ODE dp/ds=-eta[J(p+d)-J(p-d)]/(2d) converges to its unique target: the sign points toward the root and squared distance is a strict Lyapunov function away from it. THIS IS NOT A GENERAL CONVERGENCE PROOF FOR THE FINITE NOISY PROGRAM, which uses carried states, finite correlated blocks and one-sided clipping near endpoints.

## GD16: executed formation, not an oracle selecting the result

The two plants (N,M)=(1,0),(0,1) have the same complete observed baseline law at p=1, including a fixed body alarm. Nondeparting baseline observation cannot resolve their source split. Actual perturbations supply different consequences; no source label is needed by the learner. Exploration is not guaranteed harmless, since p<1 worsens the downstream twin's stationary variance.

All five conditions use seeds 840130–840161, 100 rounds, sampling dt=.2, 4000 samples per probe with first 250 discarded, randomized probe order, and continuous carried plant states. Delta=.09/(1+n/40)^.15, learning gain=.4/(1+n/25)^.5, maximum center update .06, p projected to [0,1]. Only two alarm fractions and the chosen settings enter the update. The simulator's exact OU transition calculations are not given to the learner.

Median learned p (mean of final 20 centers) and OFFLINE held-policy differential variance:
- upstream body feedback: .18137815 and .36257211 (optimum .36211952);
- downstream body feedback: .98763630 and .88746317 (optimum .87878788);
- low-noise body feedback: .98359996 and 1.23004910 (optimum 1.21969697);
- low-noise sensory feedback: .00006738 and 4.99846923;
- gradually relocated N=1-n/99,M=n/99: last-window p .98203245; variance in the final environment .89145514.

These are model values, not biological observations or consciousness scores. Add common variance 1/7 for total squared body deviation. A separate 20,000-sample frozen-policy holdout after 500 burn-in samples has differential-second-moment medians .36625,.89061,1.23605,5.01209 for the four fixed cases. Holdout data never enter learning. All seeds and all 16,000 rounds are retained locally. The learned representative is an average of final centers, not a perfect finite-horizon optimum. Probing and finite noise cause residual loss, particularly at boundary optima.

## GD17: the actual precision of binary feedback

At held stationary p and nonzero lag l, let a_j=1+2rV_j and c_j(l) be each independent common/difference covariance. Then

 Cov(A0,Al)=product_j [a_j^2-4r^2 c_j(l)^2]^(-1/2)-product_j a_j^(-1).

The finite-record alarm variance is J(1-J)/m+2/m^2 sum_(l=1)^(m-1)(m-l)Cov(A0,Al). The proof is a Gaussian exponential integral and conditional independence of comparator randomness. In the checked example, treating 128 observations as independent understates variance by factor 3.0473715. An 8192-record Monte Carlo check agrees within reported sampling variation. This is a fixed-stationary-law calculation, not an automatic confidence bound for adaptive probe blocks.

## Scope, prior art, review and failures

Extremum seeking (Krstic and Wang 2000; Stankovic and Stipanovic 2010), homeostatic reinforcement learning (Keramati and Gutkin 2014), reward-input tampering (Everitt et al. 2021), REGI (Mugler et al. 2016), and learned body models are explicit precedents. The sensory-muting example does not refute richer active-inference accounts with homeostatic preferences and epistemic terms. Targeted source review is not global priority certification.

The initial pilot used a differential-only monitor; final claims instead use whole-body alarms. Two execution timeouts were resolved with equivalent scalar updates and separately executed conditions; interrupted output was discarded. The final six primary files reproduced byte-for-byte under the fixed seeds. Seed repetition is computational reproduction, not independent scientific replication.

No experienced ownership, unity, human self-report, biological developmental order, subject count or consciousness threshold is measured. The body-to-evaluator relation must still be explained if it too becomes adaptive. This checkpoint advances a formation mechanism, not the origin of all values or phenomenology.

## Exact local artifact identities, SHA-256

RESEARCH_NOTE.md (26693 bytes): 9d30b001228084ec07d75ce4e348a0548ff923874a19412ab597d9241ca7b6cb
code/verify_adaptive_formation.py (14984 bytes): 3844eeb80a951479cc29fe26e47e5c436eb036ecbde4003b9014a7585d59cddc
code/assemble_results.py (1690 bytes): 62c8a3c44126776eb2993bc64ce6caa06582b7f3c63ab7ff59710be19ca3d1b4
results/LEARNING_RESULTS.json: 90f0c64857319cff35c07688449b7a66238e4ff4b323deca9161d51b91ce9c2a
results/LEARNING_TRACE.csv: 2f138f88867cc152376f3769dd2a45ae732a177bafb0dcc87012248a6af2cbb1
results/LEARNING_FINALS.csv: 17e22808dbba27a2735c79e2eec64b443d68503900416900752b5061c2da03e1
results/PROOF_CHECKS.json: 5b987f393914b4477cf9cad750b82e0eb037950b1fbff5ac4970e0ad821c2714
results/REPRODUCIBILITY_RECEIPT.json: 3421ab9ae72b7b96f2335491d5b4caba150b069a9c1e58a0693b78b1572a3408

Publication decision: preserve within the GD family; no new standalone DOI. Next question: an actual material or selection mechanism that keeps evaluation tied to bodily continuation while the evaluator changes, without an externally inserted 'self score'.
